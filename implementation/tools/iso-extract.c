/*
 * iso-extract -- read a binary PGM and write an ISO/IEC 19794-2:2005 template.
 *
 * Usage: iso-extract <image.pgm> <template.ist>
 *
 * This is the caller REF-011 decided this repository drives FingerJetFXOSE
 * with, in place of the sample program that ships with it.
 *
 * INV-007 F-6 measured why the sample is not used. Its header parse leaves
 * the stream one byte before the pixel data, so the buffer it hands the
 * library begins with the byte that separates the header from the pixels and
 * ends one pixel short. INV-007 F-6's arithmetic shows that the sample's own
 * short-read check can never fire on any well-formed PGM, because such a file
 * always carries exactly one byte more than the read starts short by, so the
 * program reports success and writes a template. INV-007 F-8 measured what
 * that costs: on three images the templates differ from the ones a correct
 * read produces, and the minutia counts move in both directions.
 *
 * The two values handed to the library are REF-012's, not this file's: a
 * declared resolution of 500 (REF-012 A) and the ISO output format
 * (REF-012 B). Nothing here chooses either.
 *
 * Every failure writes to standard error, returns a distinct non-zero code,
 * and leaves no output file. The ground is INV-004 B-3: the matcher already
 * in this image returns a sentinel of 4000 on internal overflow, a value in
 * the range a real score occupies, distinguished only by a warning on an
 * error stream that the same finding notes nothing here captures. A tool
 * whose failures are quiet is a tool a run can report a number from without
 * knowing the number is fabricated.
 */

#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <FJFX.h>

/*
 * Exit codes. Each failure has its own, so that a caller distinguishes them
 * without parsing a message. REF-012 C requires them to be recorded in the
 * tool's manifest entry along with the rest of the invocation.
 */
enum {
    EX_OK        = 0,
    EX_USAGE     = 2,   /* wrong number of arguments */
    EX_OPEN      = 3,   /* the input cannot be opened or read */
    EX_MAGIC     = 4,   /* the magic is not P5 */
    EX_HEADER    = 5,   /* the header ends early, or a field is not a number */
    EX_MAXVAL    = 6,   /* the maximum value is not 255 */
    EX_DIMENSION = 7,   /* width or height is zero or above 65535 */
    EX_SHORT     = 8,   /* fewer pixel bytes than width * height */
    EX_TRAILING  = 9,   /* bytes present after the pixel data */
    EX_MEMORY    = 10,  /* an allocation failed */
    EX_EXTRACT   = 11,  /* the library refused the image */
    EX_WRITE     = 12   /* the template could not be written */
};

/* REF-012 A. Not this file's value to choose, and not an argument. */
#define DECLARED_DPI 500

static int is_pgm_space(int c)
{
    return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v'
        || c == '\f';
}

/*
 * Skip whitespace and comments in a PGM header.
 *
 * A '#' comment is accepted and runs to the end of the line, which is what
 * the format says it does, rather than being refused. Both were open. This
 * one was taken because the reason this file exists at all is that the
 * upstream reader is wrong about the format, and refusing a construct the
 * format allows would be a second way of being wrong about it. INV-007 F-7
 * measured that the writer in this image emits no comment, so on this
 * repository's own path the branch is never taken; the test exercises it so
 * that it is not merely asserted.
 */
static size_t skip_space_and_comments(const unsigned char *data, size_t len,
                                      size_t pos)
{
    for (;;) {
        while (pos < len && is_pgm_space(data[pos])) {
            pos++;
        }
        if (pos < len && data[pos] == '#') {
            while (pos < len && data[pos] != '\n') {
                pos++;
            }
            continue;
        }
        return pos;
    }
}

/* Read one unsigned decimal field. Returns EX_OK, or EX_HEADER. */
static int read_field(const unsigned char *data, size_t len, size_t *pos,
                      unsigned long *out)
{
    size_t start;
    unsigned long value = 0;

    *pos = skip_space_and_comments(data, len, *pos);
    start = *pos;
    while (*pos < len && data[*pos] >= '0' && data[*pos] <= '9') {
        unsigned long digit = (unsigned long)(data[*pos] - '0');
        if (value > (ULONG_MAX - digit) / 10) {
            return EX_HEADER;
        }
        value = value * 10 + digit;
        (*pos)++;
    }
    if (*pos == start) {
        return EX_HEADER;
    }
    *out = value;
    return EX_OK;
}

/*
 * Parse a binary PGM held entirely in memory. This is the reader.
 *
 * The whole file is in memory so that "the pixel data ends where the file
 * ends" is a comparison of two lengths rather than a property of a stream.
 * That is what makes the two length checks below able to fire at all; the
 * check INV-007 F-6 examined could not, because it was asked of a stream.
 *
 * On success *out_pixels points into data at the first pixel byte, and there
 * are exactly (*out_w * *out_h) bytes from there to the end of the buffer.
 */
static int pgm_parse(const unsigned char *data, size_t len,
                     unsigned int *out_w, unsigned int *out_h,
                     const unsigned char **out_pixels)
{
    size_t pos;
    unsigned long width, height, maxval;
    size_t pixels;
    int rc;

    if (len < 2 || data[0] != 'P' || data[1] != '5') {
        return EX_MAGIC;
    }
    pos = 2;

    if ((rc = read_field(data, len, &pos, &width)) != EX_OK) {
        return rc;
    }
    if ((rc = read_field(data, len, &pos, &height)) != EX_OK) {
        return rc;
    }
    if ((rc = read_field(data, len, &pos, &maxval)) != EX_OK) {
        return rc;
    }

    /*
     * Exactly one whitespace byte separates the maximum value from the pixel
     * data, and it is consumed exactly once. This single line is the whole of
     * the defect INV-007 F-6 measured; everything else in this function is
     * ordinary parsing.
     */
    if (pos >= len || !is_pgm_space(data[pos])) {
        return EX_HEADER;
    }
    pos++;

    if (maxval != 255) {
        return EX_MAXVAL;
    }
    if (width == 0 || height == 0 || width > 0xFFFF || height > 0xFFFF) {
        return EX_DIMENSION;
    }

    pixels = (size_t)width * (size_t)height;
    if (len - pos < pixels) {
        return EX_SHORT;
    }
    if (len - pos > pixels) {
        return EX_TRAILING;
    }

    *out_w = (unsigned int)width;
    *out_h = (unsigned int)height;
    *out_pixels = data + pos;
    return EX_OK;
}

static const char *message_for(int rc)
{
    switch (rc) {
    case EX_MAGIC:     return "not a binary PGM: the magic is not P5";
    case EX_HEADER:    return "malformed PGM header";
    case EX_MAXVAL:    return "the maximum value is not 255";
    case EX_DIMENSION: return "width or height is zero or above 65535";
    case EX_SHORT:     return "fewer pixel bytes than width times height";
    case EX_TRAILING:  return "bytes present after the pixel data";
    default:           return "unrecognised parse failure";
    }
}

/* Read a whole file into memory. Returns EX_OK, EX_OPEN or EX_MEMORY. */
static int read_whole_file(const char *path, unsigned char **out, size_t *len)
{
    FILE *fp;
    unsigned char *buf = NULL;
    size_t cap = 0, used = 0;

    fp = fopen(path, "rb");
    if (fp == NULL) {
        fprintf(stderr, "iso-extract: cannot open %s: %s\n", path,
                strerror(errno));
        return EX_OPEN;
    }
    for (;;) {
        size_t got;
        if (used == cap) {
            size_t next = (cap == 0) ? (size_t)(1u << 16) : cap * 2;
            unsigned char *grown = realloc(buf, next);
            if (grown == NULL) {
                free(buf);
                fclose(fp);
                fprintf(stderr, "iso-extract: out of memory reading %s\n",
                        path);
                return EX_MEMORY;
            }
            buf = grown;
            cap = next;
        }
        got = fread(buf + used, 1, cap - used, fp);
        used += got;
        if (got == 0) {
            break;
        }
    }
    if (ferror(fp)) {
        free(buf);
        fclose(fp);
        fprintf(stderr, "iso-extract: cannot read %s: %s\n", path,
                strerror(errno));
        return EX_OPEN;
    }
    fclose(fp);
    *out = buf;
    *len = used;
    return EX_OK;
}

int main(int argc, char **argv)
{
    unsigned char *data = NULL;
    const unsigned char *pixels = NULL;
    size_t len = 0;
    unsigned int width = 0, height = 0;
    unsigned char tmpl[FJFX_FMD_BUFFER_SIZE];
    unsigned int size = (unsigned int)sizeof tmpl;
    FILE *out;
    int rc, err;

    if (argc != 3) {
        fprintf(stderr,
                "iso-extract: read a binary PGM, write an "
                "ISO/IEC 19794-2:2005 template\n"
                "usage: %s <image.pgm> <template.ist>\n"
                "  the image is 8-bit greyscale, binary PGM (P5), "
                "maximum value 255\n"
                "  the declared resolution is %d dpi and is not an argument\n",
                argv[0], DECLARED_DPI);
        return EX_USAGE;
    }

    rc = read_whole_file(argv[1], &data, &len);
    if (rc != EX_OK) {
        return rc;
    }

    rc = pgm_parse(data, len, &width, &height, &pixels);
    if (rc != EX_OK) {
        fprintf(stderr, "iso-extract: %s: %s\n", argv[1], message_for(rc));
        free(data);
        return rc;
    }

    /*
     * The resolution and the format below are REF-012 A and REF-012 B.
     *
     * The whole library is marked deprecated at its own header, quoted at
     * INV-007 F-5, so the compiler warns at every call site. That warning is
     * about the library's standing upstream, which REF-011 decided this
     * repository accepts; it says nothing about this call, so it is silenced
     * here and nowhere wider.
     */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
    err = fjfx_create_fmd_from_raw(pixels, DECLARED_DPI,
                                   (unsigned short)height,
                                   (unsigned short)width,
                                   FJFX_FMD_ISO_19794_2_2005, tmpl, &size);
#pragma GCC diagnostic pop
    free(data);
    if (err != FJFX_SUCCESS) {
        fprintf(stderr,
                "iso-extract: %s: extraction failed, the library returned "
                "%d\n", argv[1], err);
        return EX_EXTRACT;
    }

    /*
     * The output file is created only once the extraction has succeeded, so
     * that a failure leaves nothing behind for a later step to pick up and
     * report a number from.
     */
    out = fopen(argv[2], "wb");
    if (out == NULL) {
        fprintf(stderr, "iso-extract: cannot create %s: %s\n", argv[2],
                strerror(errno));
        return EX_WRITE;
    }
    if (fwrite(tmpl, 1, size, out) != size || fclose(out) != 0) {
        fprintf(stderr, "iso-extract: cannot write %s: %s\n", argv[2],
                strerror(errno));
        remove(argv[2]);
        return EX_WRITE;
    }
    return EX_OK;
}
