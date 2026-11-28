# Audit driver for uj48: follows PDF-MAP-reduction-meta.Rmd (lines 68-71, 232-233). No author file is edited.
setwd("/home/claude/work/uj48")
source('./scripts/libraries.R')
source('./scripts/functions.R')
source('./scripts/load-data.R')
source('./scripts/models-and-constants.R')
word <- FALSE
ex <- parse('./scripts/table-one-meta.R')
for (i in 1:3) eval(ex[[i]], globalenv())   # two source() calls, then meta_table <- bind_rows(...)
stopifnot(is.data.frame(meta_table))
print(meta_table)
get <- function(a) { v <- meta_table$Delta[meta_table$Approach == a]; stopifnot(length(v) == 1); v }
jsonlite::write_json(list(t1_overall = get("Overall"), t1_choice_arch = get("Choice Architecture"), t1_psychology = get("Psychology")),
  "/home/claude/AI-autonomous-research/runs/uj48-meat-meta/outputs/results.json", auto_unbox = TRUE, digits = NA)
writeLines(capture.output(sessionInfo()), "/home/claude/AI-autonomous-research/runs/uj48-meat-meta/outputs/sessionInfo.txt")
