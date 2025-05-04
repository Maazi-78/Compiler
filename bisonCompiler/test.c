#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(int argc, char **argv) {
  DIR *d = opendir("./tests");
  struct dirent *f;

  int passed = 0, failed = 0;
  char cmd[256];
  char path[256];

  clock_t t_start = clock();
  while ((f = readdir(d))) {
    if (strstr(f->d_name, ".dcf")) {
      snprintf(path, sizeof(path), "tests/%s", f->d_name);
      snprintf(cmd, sizeof(cmd), "./parser < %s > tmp.out 2>&1", path);
      system(cmd);

      FILE *out = fopen("tmp.out", "r");
      if (!out)
        continue;
      char line[256];
      int is_error = 0;
      while (fgets(line, sizeof(line), out)) {
        if (strstr(line, "Error: syntax error")) {
          is_error = 1;
          break;
        }
      }
      fclose(out);

      if (is_error) {
        printf(" ❌Failed: %s\n", path);
        failed++;
      } else
        passed++;
    }
  }
  clock_t t_end = clock();

  closedir(d);
  remove("tmp.out");

  if (failed == 0) {
    printf("✔ Passed %d test cases in %fs", passed,
           (double)(t_end - t_start) / CLOCKS_PER_SEC);
    return 0;
  } else {
    printf("Failed %d/%d test cases in %fs", failed, failed + passed,
           (double)(t_end - t_start) / CLOCKS_PER_SEC);
    return 1;
  }
}
