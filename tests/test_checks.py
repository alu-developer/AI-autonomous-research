from airesearch.checks import confirm_in_text, flagged_lines

TABLE = """Table 3: Effects on consumption
                      (1)        (2)
Treatment           0.214***   0.198**
                   (0.051)    (0.077)
Female head        \u22120.031     0.012
"""


def test_confirm_exact_value():
    assert confirm_in_text(TABLE, "0.214")
    assert confirm_in_text(TABLE, "-0.031")  # unicode minus normalized


def test_confirm_rejects_partial_and_absent():
    assert not confirm_in_text(TABLE, "0.21")   # prefix of 0.214 must not match
    assert not confirm_in_text(TABLE, "0.14")   # suffix inside 0.214 must not match
    assert not confirm_in_text(TABLE, "0.300")


def test_confirm_near_label():
    assert confirm_in_text(TABLE, "0.198", near="Treatment")
    assert not confirm_in_text(TABLE, "0.214", near="Female head")


DIFF = """--- a/analysis.R
+++ b/analysis.R
@@ -1,4 +1,5 @@
-setwd("C:/Users/x")
+setwd("/work")
+library(dplyr)
 m1 <- lm(y ~ treat, data = d)
-m2 <- lm(y ~ treat + age, data = d)
+m2 <- lm(y ~ treat, data = d)
+# lm( in a comment is fine
"""


def test_diff_flags_only_estimation_changes():
    flags = flagged_lines(DIFF)
    assert len(flags) == 2
    assert all("lm(" in f for f in flags)


def test_diff_clean_environment_fix():
    clean = "--- a/x.R\n+++ b/x.R\n@@\n-setwd('C:/a')\n+setwd('/w')\n+library(jsonlite)\n"
    assert flagged_lines(clean) == []


def test_diff_flags_stata_sample_change():
    d = "--- a/m.do\n+++ b/m.do\n@@\n+drop if age > 60\n reg y x\n"
    assert flagged_lines(d)
