# Audit runner: evaluates the script's top-level expressions in order, unchanged, and stops after
# the first expression that starts at or after line `stop_line`; then runs the script's appended audit block.
args <- commandArgs(trailingOnly=TRUE); f <- normalizePath(args[1]); stop_line <- as.integer(args[2])
setwd(dirname(f)); exprs <- parse(f, keep.source=TRUE); sr <- attr(exprs, "srcref")
audit_start <- grep("appended by reproduction audit", readLines(f))[1]
for (i in seq_along(exprs)) {
  l <- sr[[i]][1]
  if (l > stop_line && l < audit_start) next
  tryCatch(print(eval(exprs[[i]], globalenv())), error=function(e) message("AUDIT-ERROR expr ", i, " line ", l, ": ", conditionMessage(e)))
}
message("AUDIT-DONE")
