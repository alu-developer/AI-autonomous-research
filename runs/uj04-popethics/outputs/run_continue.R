# Audit runner: evaluates each top-level expression of the script in order; logs errors and continues.
args <- commandArgs(trailingOnly=TRUE); setwd(dirname(normalizePath(args[1])))
exprs <- parse(args[1]); nerr <- 0
for (i in seq_along(exprs)) tryCatch(print(eval(exprs[[i]], globalenv())), error=function(e){nerr <<- nerr+1; message("AUDIT-ERROR expr ", i, ": ", conditionMessage(e))})
message("AUDIT-DONE errors=", nerr)
