# Audit runner: evaluates each top-level expression of the script in order; logs errors and continues.
# Runner state lives in its own environment, so a script's rm(list = ls()) cannot remove it.
.audit <- new.env(parent = emptyenv())  # hidden name: rm(list = ls()) does not remove it
.audit$args <- commandArgs(trailingOnly = TRUE)
setwd(dirname(normalizePath(.audit$args[1])))
.audit$exprs <- parse(.audit$args[1]); .audit$nerr <- 0
for (.audit_i in seq_along(.audit$exprs)) {
  .audit$i <- .audit_i
  tryCatch(print(eval(.audit$exprs[[.audit$i]], globalenv())),
           error = function(e) { .audit$nerr <- .audit$nerr + 1; message("AUDIT-ERROR expr ", .audit$i, ": ", conditionMessage(e)) })
}
message("AUDIT-DONE errors=", .audit$nerr)
