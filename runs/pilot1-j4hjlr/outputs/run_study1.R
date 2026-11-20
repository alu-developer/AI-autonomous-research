# Study 1. Net zero policies in German and UK municipalities
# Tables 1-2, A1-A5, B1-B6; Figures B1-B2.

library(dplyr)
library(tidyr)
library(purrr)
library(stringr)
library(tibble)
library(ggplot2)
library(broom)
library(fixest)
library(knitr)
library(stargazer)

## Working directory and output folders
setwd("/home/claude/pilot/j4hjlr")

## Study 1 data: UK observations and German-sender observations
# Local vote share: Labour in the UK and Green in Germany.
uk <- read.csv("rep_uk_data.csv") %>%
  filter(scientist == 0) %>%
  mutate(area = country)
de <- read.csv("rep_de_data.csv") %>% 
  filter(de_politician == 1,
         scientist == 0)  %>%
  mutate(vote_share = green_share,
         dist_500km = dist_100km/5)


## Table 1 and Table B1. German experiment, without and with covariates
de_exp <- read.csv("rep_de_data.csv") %>%
  filter(scientist == 0)

exp1 <- lm(any_clicks ~ de_politician, de_exp)
exp2 <- lm(all_clicks ~ de_politician, de_exp)
exp3 <- lm(commit ~ de_politician, de_exp)
exp1c <- lm(any_clicks ~ de_politician + long_term + green_share + copartisan + log(pop), de_exp)
exp2c <- lm(all_clicks ~ de_politician + long_term + green_share + copartisan + log(pop), de_exp)
exp3c <- lm(commit ~ de_politician + long_term + green_share + copartisan + log(pop), de_exp)


### Table 1
stargazer(exp1,exp1c,exp2,exp2c,exp3,exp3c,no.space=T,
          keep = "de_politician", star.cutoffs = c(.05,.01,.001), type = "text",
          covariate.labels = "German politician",
          add.lines = list(c("Covariate adjustment","No","Yes","No","Yes","No","Yes")))


### Table B1
stargazer(exp1,exp1c,exp2,exp2c,exp3,exp3c,no.space=T,
          star.cutoffs = c(.05,.01,.001), type = "text")


## Table 2. Pooled observational models, full sample and within 200 km
# Pool Data
uk$state<-uk$country
uk$country<-'uk'
pooled <- de %>%
  dplyr::select(any_clicks, all_clicks, commit, dist_100km, country, copartisan, pop, vote_share,
                industry_share_broad, industry_share_no_construction) %>%
  bind_rows(uk %>%
              dplyr::select(any_clicks, all_clicks, commit, dist_100km, country, copartisan, pop, vote_share, state,
                            industry_share_broad, industry_share_no_construction) %>%
              mutate(country = "uk"))


## Industrial employment shares: B-E in Table 2; B-F in Table B3.
## Main measure: B-E share (mining, manufacturing, energy, water/waste),
## excluding construction. Robustness below uses B-F, including construction.

summary(p1_ind<-lm(any_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                     industry_share_no_construction, pooled))
summary(p2_ind<-lm(all_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                     industry_share_no_construction, pooled))
summary(p3_ind<-lm(commit ~ dist_100km + log(pop) + vote_share+copartisan+country+
                     industry_share_no_construction, pooled))

summary(p1c_ind<-lm(any_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                      industry_share_no_construction, pooled[pooled$dist_100km<=2,]))
summary(p2c_ind<-lm(all_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                      industry_share_no_construction, pooled[pooled$dist_100km<=2,]))
summary(p3c_ind<-lm(commit ~ dist_100km + log(pop) + vote_share+copartisan+country+
                      industry_share_no_construction, pooled[pooled$dist_100km<=2,]))

stargazer(p1_ind,p1c_ind,p2_ind,p2c_ind,p3_ind,p3c_ind,
          no.space=T,star.cutoffs = c(.05, .01, 0.001), type="text")

####### APPENDIX ########----------------------------

## Table A1. Opening rates in the German experiment available in original study

## Table A2. Outcome descriptives, experimental and observational samples
study1_outcome_desc <- bind_rows(
  tibble(
    Sample = "Experimental",
    Group = "All",
    Outcome = c("Policy Interest", "Policy Engagement", "Policy Commitments"),
    N = c(sum(!is.na(de_exp$any_clicks)),
          sum(!is.na(de_exp$all_clicks)),
          sum(!is.na(de_exp$commit))),
    Mean = c(mean(de_exp$any_clicks, na.rm = T),
             mean(de_exp$all_clicks, na.rm = T),
             mean(de_exp$commit, na.rm = T)),
    SD = c(sd(de_exp$any_clicks, na.rm = T),
           sd(de_exp$all_clicks, na.rm = T),
           sd(de_exp$commit, na.rm = T)),
    Min = c(min(de_exp$any_clicks, na.rm = T),
            min(de_exp$all_clicks, na.rm = T),
            min(de_exp$commit, na.rm = T)),
    Max = c(max(de_exp$any_clicks, na.rm = T),
            max(de_exp$all_clicks, na.rm = T),
            max(de_exp$commit, na.rm = T))
  ),
  de_exp %>%
    mutate(Group = ifelse(de_politician == 1, "German sender", "UK sender")) %>%
    group_by(Group) %>%
    summarise(
      Sample = "Experimental",
      N_interest = sum(!is.na(any_clicks)),
      Mean_interest = mean(any_clicks, na.rm = T),
      SD_interest = sd(any_clicks, na.rm = T),
      Min_interest = min(any_clicks, na.rm = T),
      Max_interest = max(any_clicks, na.rm = T),
      N_engagement = sum(!is.na(all_clicks)),
      Mean_engagement = mean(all_clicks, na.rm = T),
      SD_engagement = sd(all_clicks, na.rm = T),
      Min_engagement = min(all_clicks, na.rm = T),
      Max_engagement = max(all_clicks, na.rm = T),
      N_commit = sum(!is.na(commit)),
      Mean_commit = mean(commit, na.rm = T),
      SD_commit = sd(commit, na.rm = T),
      Min_commit = min(commit, na.rm = T),
      Max_commit = max(commit, na.rm = T)
    ) %>%
    pivot_longer(cols = c(N_interest:Max_commit),
                 names_to = c(".value", "Outcome"),
                 names_sep = "_") %>%
    mutate(Outcome = recode(Outcome,
                            "interest" = "Policy Interest",
                            "engagement" = "Policy Engagement",
                            "commit" = "Policy Commitments")) %>%
    select(Sample, Group, Outcome, N, Mean, SD, Min, Max),
  tibble(
    Sample = "Observational",
    Group = "All",
    Outcome = c("Policy Interest", "Policy Engagement", "Policy Commitments"),
    N = c(sum(!is.na(pooled$any_clicks)),
          sum(!is.na(pooled$all_clicks)),
          sum(!is.na(pooled$commit))),
    Mean = c(mean(pooled$any_clicks, na.rm = T),
             mean(pooled$all_clicks, na.rm = T),
             mean(pooled$commit, na.rm = T)),
    SD = c(sd(pooled$any_clicks, na.rm = T),
           sd(pooled$all_clicks, na.rm = T),
           sd(pooled$commit, na.rm = T)),
    Min = c(min(pooled$any_clicks, na.rm = T),
            min(pooled$all_clicks, na.rm = T),
            min(pooled$commit, na.rm = T)),
    Max = c(max(pooled$any_clicks, na.rm = T),
            max(pooled$all_clicks, na.rm = T),
            max(pooled$commit, na.rm = T))
  )
) %>%
  mutate(
    Sample = factor(Sample, levels = c("Experimental", "Observational")),
    Outcome = factor(Outcome, levels = c("Policy Interest", "Policy Engagement", "Policy Commitments")),
    Group = factor(Group, levels = c("All", "German sender", "UK sender"))
  ) %>%
  arrange(Sample, Outcome, Group) %>%
  mutate(across(c(Sample, Outcome, Group), as.character))

print(kable(study1_outcome_desc,format="markdown",booktabs=T,digits=3))

## Table A3. German observational sample: state, gender, and party
de_desc <- de %>%
  transmute(Bundesland = bundesland,
            Gender = ifelse(female == 1,"Female",ifelse(female == 0,"Male",NA)),
            Party = party_clean) %>%
  pivot_longer(everything(),names_to="Variable",values_to="Level") %>%
  filter(!is.na(Level)) %>%
  count(Variable,Level,name="N") %>%
  group_by(Variable) %>%
  mutate(Percent = 100*N/sum(N)) %>%
  ungroup() %>%
  arrange(Variable,desc(N))
print(kable(de_desc,format="markdown",booktabs=T,digits=1))

## Table A4. UK observational sample: party, area, and gender
uk_desc <- uk %>%
  mutate(party_label = str_to_lower(str_trim(Party)),
         party_label = case_when(
           party_label == "conservative" ~ "Conservative",
           party_label %in% c("labour","scottish labour") ~ "Labour",
           party_label == "liberal democrats" ~ "Liberal Democrats",
           party_label %in% c("ind","independent","independents") ~ "Independent",
           party_label == "plaid cymru" ~ "Plaid Cymru",
           party_label %in% c("green","green party") ~ "Green Party",
           party_label %in% c("snp","scottish national party") ~ "SNP",
           party_label == "ukip" ~ "Ukip",
           .default = "NR/Other")) %>%
  transmute(Party = party_label, Area = area,
            Gender = ifelse(female == 1,"Female",ifelse(female == 0,"Male",NA))) %>%
  pivot_longer(everything(),names_to="Variable",values_to="Level") %>%
  filter(!is.na(Level)) %>%
  count(Variable,Level,name="N") %>%
  group_by(Variable) %>%
  mutate(Percent = 100*N/sum(N)) %>%
  ungroup() %>%
  arrange(Variable,desc(N))
print(kable(uk_desc,format="markdown",booktabs=T,digits=1))

## Table A5. Covariate balance in the German experiment
de_exp <- de_exp %>%
  mutate(pop_log = log(pop))

treat_var <- "de_politician"                      
vars      <- c("female", "pop_log", "left", "right",
               "CDU_share", "green_share", "copartisan")

balance_row <- function(v){
  # Welch t-test
  tt  <- t.test(reformulate(treat_var, v), data = de_exp)
  
  tibble(
    variable      = v,
    control_mean  = tt$estimate[1],          # group 0
    treat_mean    = tt$estimate[2],          # group 1
    p_value       = tt$p.value
  )
}

balance_tbl <- map_dfr(vars, balance_row) %>%
  mutate(across(c(control_mean, treat_mean, p_value), round, 3))

print(kable(balance_tbl,format="markdown",booktabs=T,digits=3))

## Table B2. Observational models within 150 km and 250 km
summary(p4c<-lm(any_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country, pooled[pooled$dist_100km<=1.5,]))
summary(p5c<-lm(all_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country, pooled[pooled$dist_100km<=1.5,]))
summary(p6c<-lm(commit ~ dist_100km + log(pop) + vote_share+copartisan+country, pooled[pooled$dist_100km<=1.5,]))
summary(p7c<-lm(any_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country, pooled[pooled$dist_100km<=2.5,]))
summary(p8c<-lm(all_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country, pooled[pooled$dist_100km<=2.5,]))
summary(p9c<-lm(commit ~ dist_100km + log(pop) + vote_share+copartisan+country, pooled[pooled$dist_100km<=2.5,]))

stargazer(p4c,p5c,p6c,p7c,p8c,p9c,no.space=T,star.cutoffs = c(.05, .01, 0.001), type="text")


## Table B3. Broad industrial employment control (B-F), including construction.

summary(p1_ind_broad<-lm(any_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                           industry_share_broad, pooled))
summary(p2_ind_broad<-lm(all_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                           industry_share_broad, pooled))
summary(p3_ind_broad<-lm(commit ~ dist_100km + log(pop) + vote_share+copartisan+country+
                           industry_share_broad, pooled))

summary(p1c_ind_broad<-lm(any_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                            industry_share_broad, pooled[pooled$dist_100km<=2,]))
summary(p2c_ind_broad<-lm(all_clicks ~ dist_100km + log(pop) + vote_share+copartisan+country+
                            industry_share_broad, pooled[pooled$dist_100km<=2,]))
summary(p3c_ind_broad<-lm(commit ~ dist_100km + log(pop) + vote_share+copartisan+country+
                            industry_share_broad, pooled[pooled$dist_100km<=2,]))

broad_models <- list(p1_ind_broad,p1c_ind_broad,p2_ind_broad,p2c_ind_broad,p3_ind_broad,p3c_ind_broad)
stargazer(broad_models,
          no.space=T,star.cutoffs = c(.05, .01, 0.001), type="text")


## Figure B1. Distance associations by industrial employment quartile

pooled <- pooled %>%
  mutate(
    industry_cat = cut(
      industry_share_no_construction,
      breaks  = quantile(industry_share_no_construction, probs = seq(0, 1, .25), na.rm = T),
      include.lowest = T
    )
  )

other_covariates <- "log(pop) + industry_share_no_construction + copartisan + vote_share + country"
dvs <- c("any_clicks", "all_clicks", "commit")

industry_results <- pooled %>% 
  filter(!is.na(industry_cat)) %>%
  group_by(industry_cat) %>% 
  group_modify(~{
    map_dfr(dvs, function(dv) {
      rhs <- paste("dist_100km", other_covariates, sep = " + ")
      fmla <- as.formula(paste(dv, "~", rhs))
      
      fit <- lm(fmla, data = .x)
      
      tidy(fit, conf.int = TRUE) %>% 
        filter(term == "dist_100km") %>% 
        mutate(depvar = dv,
               n = nobs(fit))
    })
  }) %>% 
  na.omit() %>%
  ungroup()

industry_results$depvar <- recode(industry_results$depvar,
                                  "any_clicks" = "Policy Interest",
                                  "all_clicks" = "Policy Engagement",
                                  "commit" = "Policy Commitments")
industry_results$depvar <- factor(industry_results$depvar,
                                  levels = c("Policy Interest", "Policy Engagement", "Policy Commitments"))

industry_plot <- ggplot(industry_results,
                        aes(x = industry_cat, y = estimate, color = depvar, shape = depvar)) +
  geom_point(position = position_dodge(width = 0.4), size = 3) +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high),
                position = position_dodge(width = 0.4), width = 0.15) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(
    x = "Industrial employment share (B-E)",
    y = "Marginal effect of distance",
    color = NULL,
    shape = NULL) +
  theme_bw() +
  geom_hline(yintercept = 0, linetype = "dotted") +
  theme(panel.grid.major = element_blank(), 
        plot.title = element_text(size = 12), 
        legend.position = "bottom",
        legend.text = element_text(size = 12)) +
  scale_color_grey()

ggsave("industry_bins.png", industry_plot, width = 7, height = 4.5, dpi = 300)



## Figure B2. Distance associations by contextual similarity quartile
## Manhattan distance across standardized population, vote share, and industrial employment

pooled_context <- pooled %>%
  group_by(country) %>%
  mutate(pop_log = log(pop),
         pop_log_z = as.numeric(scale(pop_log)),
         vote_share_z = as.numeric(scale(vote_share)),
         industry_z = as.numeric(scale(industry_share_no_construction))) %>%
  ungroup()

sender_values <- pooled_context %>%
  filter(!is.na(dist_100km)) %>%
  group_by(country) %>%
  arrange(dist_100km, .by_group = T) %>%
  summarise(pop_log_sender = first(na.omit(pop_log_z)),
            vote_share_sender = first(na.omit(vote_share_z)),
            industry_sender = first(na.omit(industry_z)))

pooled_context <- pooled_context %>%
  left_join(sender_values, by = "country") %>%
  mutate(context_dist = abs(pop_log_z - pop_log_sender) +
           abs(vote_share_z - vote_share_sender) +
           abs(industry_z - industry_sender),
         context_sim = -context_dist)

pooled_context <- pooled_context %>%
  filter(!is.na(context_sim)) %>%
  mutate(
    context_cat = cut(
      context_sim,
      breaks  = quantile(context_sim, probs = seq(0, 1, .25), na.rm = T),
      include.lowest = T,
      labels = c("Q1", "Q2", "Q3", "Q4")
    )
  )

other_covariates <- "log(pop) + vote_share + copartisan + country + industry_share_no_construction"
dvs <- c("any_clicks", "all_clicks", "commit")

context_results <- pooled_context %>% 
  filter(!is.na(context_cat)) %>%
  group_by(context_cat) %>% 
  group_modify(~{
    map_dfr(dvs, function(dv) {
      rhs <- paste("dist_100km", other_covariates, sep = " + ")
      fmla <- as.formula(paste(dv, "~", rhs))
      
      fit <- lm(fmla, data = .x)
      
      tidy(fit, conf.int = TRUE) %>% 
        filter(term == "dist_100km") %>% 
        mutate(depvar = dv,
               n = nobs(fit))
    })
  }) %>% 
  na.omit() %>%
  ungroup()

context_results$depvar <- recode(context_results$depvar,
                                  "any_clicks" = "Policy Interest",
                                  "all_clicks" = "Policy Engagement",
                                  "commit" = "Policy Commitments")
context_results$depvar <- factor(context_results$depvar,
                                  levels = c("Policy Interest", "Policy Engagement", "Policy Commitments"))

context_plot <- ggplot(context_results,
                       aes(x = context_cat, y = estimate, color = depvar, shape = depvar)) +
  geom_point(position = position_dodge(width = 0.4), size = 3) +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high),
                position = position_dodge(width = 0.4), width = 0.15) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(
    x = "Contextual similarity to sender area (quartiles)",
    y = "Marginal effect of distance",
    color = NULL,
    shape = NULL) +
  theme_bw() +
  geom_hline(yintercept = 0, linetype = "dotted") +
  theme(panel.grid.major = element_blank(), 
        plot.title = element_text(size = 12), 
        legend.position = "bottom",
        legend.text = element_text(size = 12)) +
  scale_color_grey()

ggsave("context_distance_netzero.png", context_plot, width = 7, height = 4.5, dpi = 300)



## Table B4. Bivariate observational models

summary(biv1<-lm(any_clicks ~ dist_100km, pooled))
summary(biv2<-lm(all_clicks ~ dist_100km, pooled))
summary(biv3<-lm(commit ~ dist_100km, pooled))

stargazer(biv1,biv2,biv3,no.space=T,star.cutoffs = c(.05, .01, 0.001), type="text")



## Table B5. Separate UK and German observational models
country_models <- list(
  lm(any_clicks ~ dist_100km + log(pop) + vote_share, uk),
  lm(all_clicks ~ dist_100km + log(pop) + vote_share, uk),
  lm(commit ~ dist_100km + log(pop) + vote_share, uk),
  lm(any_clicks ~ dist_100km + log(pop) + vote_share, de),
  lm(all_clicks ~ dist_100km + log(pop) + vote_share, de),
  lm(commit ~ dist_100km + log(pop) + vote_share, de)
)
stargazer(country_models, no.space=T, star.cutoffs=c(.05, .01, .001),
          type="text")

## Table B6. Regional fixed effects in Germany; municipality-clustered standard errors
# Municipality clusters are identified by the original sample's cluster variable.
de_femodels_rb <- list(
  "Interest" = feols(any_clicks ~ dist_100km + copartisan + log(pop) + vote_share |
                       region, data=de, cluster="cluster", fixef.rm="none"),
  "Engagement" = feols(all_clicks ~ dist_100km + copartisan + log(pop) + vote_share |
                         region, data=de, cluster="cluster", fixef.rm="none"),
  "Commit" = feols(commit ~ dist_100km + copartisan + log(pop) + vote_share |
                     region, data=de, cluster="cluster", fixef.rm="none")
)
print(etable(de_femodels_rb,tex=F,digits=3,
       signif.code=c("***"=.001,"**"=.01,"*"=.05)))











