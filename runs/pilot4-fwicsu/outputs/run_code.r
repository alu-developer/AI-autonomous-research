library(psych)     # for Chronbach's alpha
library(stargazer) # to make things look nice 

library(modelsummary) # for confidence intervals
library(broom)        # for confidence intervals

# load up the data

setwd("/home/claude/pilot/fwicsu")

jp <- read.csv("replication_data.csv", header=TRUE)

# total number of respondents

totalNum <- nrow(jp)

# remove those who could not answer the "are you working from home more or less" because they were not working before the pandemic

jp <- jp[!is.na(jp$workMoreHome), ]

totalAnsweredQuestion <- nrow(jp)

removedA <- totalNum - totalAnsweredQuestion

# run Cronbach's alpha to test internal consistency of our 
# separate K6 measures 

alpha(jp[, c("health_JP_core_3_1", 
             "health_JP_core_3_2", 
             "health_JP_core_3_3", 
             "health_JP_core_3_4", 
             "health_JP_core_3_5", 
             "health_JP_core_3_6")])
			 
# create reduced versions of the data set

# just those in work 

jpw <- jp[jp$working == 1 & !is.na(jp$working), ]

remainingRespondents <- nrow(jpw)

# just those working in the medical sector

jpm <- jp[jp$working == 1 & jp$industry == 6 & !is.na(jp$working) & !is.na(jp$industry), ]
			 
# just workers not in medical sector

jpnm <- jp[jp$working == 1 & jp$industry != 6 & !is.na(jp$working) & !is.na(jp$industry), ]

# descriptive statistics 

variableNames <- 
	c(
		"N (% of all)", 
		"Work from home more", 
		"Severe Psychological Distress", 
		"Women", 
		"Age", 
		"Currently married (didn't skip question)", 
		paste0("General trust (", min(jpnm$trustGeneral, na.rm=TRUE), " - ", max(jpnm$trustGeneral, na.rm=TRUE), ")"),
		paste0("Economic status (", min(jpnm$economicStatus, na.rm=TRUE), " - ", max(jpnm$economicStatus, na.rm=TRUE), ")"), 
		paste0("General health (", min(jpnm$generalHealth, na.rm=TRUE), " - ", max(jpnm$generalHealth, na.rm=TRUE), ")"), 
		paste0("Take risks (", min(jpnm$takeRisk, na.rm=TRUE), " - ", max(jpnm$takeRisk, na.rm=TRUE), ")")
	)
	
workersNonMedical <- 
	c(
		paste0(nrow(jpnm), " (", round(nrow(jpnm) / nrow(jpw)*100, 2), "%)"),
		paste0(length(jpnm$age[jpnm$workMoreHome==1]), " (", round(length(jpnm$age[jpnm$workMoreHome==1]) / length(jpnm$age)*100, 2), "%)"),  
		paste0(length(jpnm$age[jpnm$k6cutpoint==1]), " (", round(length(jpnm$age[jpnm$k6cutpoint==1]) / length(jpnm$age)*100, 2), "%)"),
		paste0(length(jpnm$age[jpnm$women==1]), " (", round(length(jpnm$age[jpnm$women==1]) / length(jpnm$age)*100, 2), "%)"),
		paste0("Mean: ", round(mean(jpnm$age), 2), ", SD: ", round(sd(jpnm$age), 2)),
		paste0(length(jpnm$age[jpnm$married==1 & !is.na(jpnm$married)]), " (", round(length(jpnm$age[jpnm$married==1 & !is.na(jpnm$married)]) / length(jpnm$age[!is.na(jpnm$married)])*100, 2), "%)"), 
		paste0("Mean: ", round(mean(jpnm$trustGeneral, na.rm=TRUE), 2), ", SD: ", round(sd(jpnm$trustGeneral, na.rm=TRUE), 2)),
		paste0("Mean: ", round(mean(jpnm$economicStatus, na.rm=TRUE), 2), ", SD: ", round(sd(jpnm$economicStatus, na.rm=TRUE), 2)), 
		paste0("Mean: ", round(mean(jpnm$generalHealth, na.rm=TRUE), 2), ", SD: ", round(sd(jpnm$generalHealth, na.rm=TRUE), 2)), 
		paste0("Mean: ", round(mean(jpnm$takeRisk, na.rm=TRUE), 2), ", SD: ", round(sd(jpnm$takeRisk, na.rm=TRUE), 2))
	)

workersMedical <- 
	c(
		paste0(nrow(jpm), " (", round(nrow(jpm) / nrow(jpw)*100, 2), "%)"),
		paste0(length(jpm$age[jpm$workMoreHome==1]), " (", round(length(jpm$age[jpm$workMoreHome==1]) / length(jpm$age)*100, 2), "%)"),  
		paste0(length(jpm$age[jpm$k6cutpoint==1]), " (", round(length(jpm$age[jpm$k6cutpoint==1]) / length(jpm$age)*100, 2), "%)"),
		paste0(length(jpm$age[jpm$women==1]), " (", round(length(jpm$age[jpm$women==1]) / length(jpm$age)*100, 2), "%)"),
		paste0("Mean: ", round(mean(jpm$age), 2), ", SD: ", round(sd(jpm$age), 2)),
		paste0(length(jpm$age[jpm$married==1 & !is.na(jpm$married)]), " (", round(length(jpm$age[jpm$married==1 & !is.na(jpm$married)]) / length(jpm$age[!is.na(jpm$married)])*100, 2), "%)"), 
		paste0("Mean: ", round(mean(jpm$trustGeneral, na.rm=TRUE), 2), ", SD: ", round(sd(jpm$trustGeneral, na.rm=TRUE), 2)),
		paste0("Mean: ", round(mean(jpm$economicStatus, na.rm=TRUE), 2), ", SD: ", round(sd(jpm$economicStatus, na.rm=TRUE), 2)), 
		paste0("Mean: ", round(mean(jpm$generalHealth, na.rm=TRUE), 2), ", SD: ", round(sd(jpm$generalHealth, na.rm=TRUE), 2)), 
		paste0("Mean: ", round(mean(jpm$takeRisk, na.rm=TRUE), 2), ", SD: ", round(sd(jpm$takeRisk, na.rm=TRUE), 2))
	)
		
							
outputTable <- data.frame(variableNames, workersNonMedical, workersMedical)
outputTable

# models

m1 <- glm(k6cutpoint ~ workMoreHome + women + age + age2 + married + trustGeneral + economicStatus + generalHealth + takeRisk, data = jpnm, family = binomial)
m2 <- glm(k6cutpoint ~ workMoreHome + women + age + age2 + married + trustGeneral + economicStatus + generalHealth + takeRisk, data = jpm, family = binomial)


stargazer(m1, m2, type="text") 

# now as confidence intervals 

# first output to screen

models <- list("Working, non-medical sector" = m1, "Working, medical sector" = m2)

modelsummary(
  models,
  exponentiate = TRUE,  # converts log-odds to odds ratios
  statistic = "({conf.low}, {conf.high})",  # 95% CI in parentheses
  gof_omit = "AIC|BIC|Log.Lik|Deviance",
  stars = FALSE,  
  fmt = 2,
  output = "markdown"
)

# now as Word doc

outdir  <- getwd()
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
outfile <- file.path(outdir, "models_output.docx")

modelsummary(
  models,
  exponentiate = TRUE,  # converts log-odds to odds ratios
  statistic = "({conf.low}, {conf.high})",  # 95% CI in parentheses
  gof_omit = "AIC|BIC|Log.Lik|Deviance",
  stars = FALSE,  
  fmt = 2,
  output = outfile
)



