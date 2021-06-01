#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "urisc_v1.h"

#include "stack.c"
#include "varlist.c"
#include "var.c"

// File stuff
char * current_file;
char * buffer = 0;

char ** code = NULL;
int lineCount = 0;
int currentLine = 0;

// Interpreter variables
struct varlist * reg;
struct varlist * labels;

// CLI Options
int minify = 0;
int verbose = 0;

void error(char * text, char * buffer, int pos)
{
    // int MAXLINE = 128;

    printf("\nProgram execution terminated:\n\n");

    if (buffer == NULL || pos < 0)
    {
        printf("(At %s)\n", current_file);
    }
    else
    {
        char * linepreview = malloc(5 + 1);
        linepreview[0] = buffer[pos - 2];
        linepreview[1] = buffer[pos - 1];
        linepreview[2] = buffer[pos];
        linepreview[3] = buffer[pos + 1];
        linepreview[4] = buffer[pos + 2];
        linepreview[5] = 0;

        printf("At %s : Pos %d\n\n", current_file, pos);
        printf("> {{ %s }}\n\n", linepreview);

        free(linepreview);
    }

    printf("Error: %s\n\n", text);

    quit(1);
}

// Strip a string of carriage returns from the right hand side only
// (Returns new string length)
int rstripCarriageReturns(char * _str, int _len)
{
    int i = _len;

    while (_str[i--] == '\r');

    _str[i] = '\0';

    return i;
}

char * minify_code(char * code)
{
    int len = strlen(code);
    char * min = malloc(len + 1);
    min[0] = 0;
    int ind = 0;

    int comment = 0;

    for (int i = 0; i < len; i++)
    {
        if (code[i] == '#')
            comment = 1;
        else if (code[i] == '\n')
            comment = 0;

        if (comment)
            continue;

        if (code[i] == '0' || code[i] == '1')
            min[ind++] = code[i];
    }

    min[ind] = 0;
    return min;
}

void quit(int code)
{
    free(reg->names);
    free(reg->values);
    free(reg);

    free(buffer);

    exit(code);
}

int main(int argc, char ** argv)
{
    char ** args = malloc(argc * sizeof(char *));
    int newargc = 0;

    for (int i = 1; i < argc; i++)
    {
        if (!strcmp(argv[i], "-v") || !strcmp(argv[i], "--version"))
        {
            printf("Char %s\n", VERSION);
            free(args);
            return 0;
        }
        // if (!strcmp(argv[i], "-m") || !strcmp(argv[i], "--minify"))
        //     minify = 1;
        if (!strcmp(argv[i], "-V") || !strcmp(argv[i], "--verbose"))
            verbose = 1;
        else
        {
            args[newargc] = argv[i];
            newargc++;
        }
    }

    if (!newargc)
        return 0;

    current_file = args[0];

    long length;
    FILE * f = fopen(current_file, "rb");

    if (!f)
    {
        printf("File at path '%s' does not exist or is not accessible\n", current_file);
        return 1;
    }

    fseek(f, 0, SEEK_END);
    length = ftell(f);
    fseek(f, 0, SEEK_SET);
    buffer = malloc(length);
    if (buffer)
        fread(buffer, 1, length, f);
    fclose(f);

    if (!buffer)
        return 0;

    lineCount = 0;
    for (int i = 0; i < length; i++)
        lineCount += (buffer[i] == '\n');

    // Minify the whole program before running it
    // char * minified = minify_code(buffer);
    // free(buffer);

    // Buffer now contains minified code
    // buffer = minified;
    // length = strlen(buffer);

    // if (minify)
    // {
    //     printf("%s\n", buffer);
    //     free(buffer);
    //     return 0;
    // }

    free(args);

    // Interpreter vars
    reg = newVarlist(64); // Block size is 64
    labels = newVarlist(32); // Block size is 32

    // Fetch lines of code
    int i = 0;
    code = malloc(lineCount * sizeof(char *));

    char * filePtr = strtok(buffer, "\n");
    while (filePtr != NULL)
    {
        code[i] = filePtr;
        int len = strlen(code[i]);
        len = rstripCarriageReturns(code[i], len);

        // Define labels
        if (len == 1)
            varlistAdd(labels, code[i][0], i);

        filePtr = strtok(NULL, "\n");
        i++;
    }

    // (currentLine is global)
    for (currentLine = 0; currentLine < lineCount; currentLine++)
    {
        char * line = code[currentLine];
        int len = strlen(line);
        printf("::%d\n", len);

        if (verbose)
            printf("%s\n", line);

        if (len >= 2)
        {
            // Flip bit
            int newVal = !varlistGet(reg, line[0]);
            printf("{%d}\n", newVal);
            varlistAdd(reg, line[0], newVal);

            // Jump
            if (newVal)
                currentLine = varlistGetDef(labels, line[1], currentLine);
        }
    }

    for (int i = 0; i < reg->size; i++)
        printf("[%c:%d]\n", reg->names[i], reg->values[i]);

    quit(0);

    return 0;
}