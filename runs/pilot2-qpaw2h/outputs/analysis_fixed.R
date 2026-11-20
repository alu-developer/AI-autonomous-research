################################################################
# REPLICATION SCRIPT
# Soil Nutrient Stress, Crop System Composition, and
# Agro-Climatic Confounding: A District-Level Analysis of
# Maharashtra's Agricultural Soils
#
# Author: Prakash Vhankade
# Gokhale Institute of Politics and Economics (GIPE), Pune
#
# This script reproduces all tables, figures, and statistics
# reported in the manuscript, starting from the four
# district-level analytical datasets provided in /data.
#
# Raw SHC microdata (551,955 district-aggregated records) are
# not redistributed in this package because they are publicly
# available at soilhealth.dac.gov.in. This script begins from
# the district-aggregated files already constructed from that
# source.
################################################################

library(dplyr)
library(tidyr)
library(quantreg)
library(vars)
library(sf)
library(ggplot2)
select <- dplyr::select  # DEVIATION by auditor: fix namespace masking

# Set working directory to the package root before running
# setwd("path/to/replication_package")

# ===============================================================
# SECTION 0: LOAD DATA
# ===============================================================

snsi_final      <- read.csv("data/snsi_final.csv")
master_v3       <- read.csv("data/master_v3_rainfall.csv")
pc_scores       <- read.csv("data/pc_scores.csv")
cluster_profiles<- read.csv("data/cluster_profiles.csv")

cat("Data loaded:\n")
cat("  snsi_final:", nrow(snsi_final), "rows (34 districts x 2 cycles)\n")
cat("  master_v3:", nrow(master_v3), "rows (34 districts, full predictor set)\n")
cat("  pc_scores:", nrow(pc_scores), "rows\n")
cat("  cluster_profiles:", nrow(cluster_profiles), "rows\n\n")


# ===============================================================
# SECTION 4.1: SOIL NUTRIENT STRESS PATTERNS (TABLE 1)
# ===============================================================

cat("=== TABLE 1: SNSI stress category distribution ===\n")

table1 <- snsi_final %>%
  group_by(year, stress_category) %>%
  summarise(n = n(), mean_SNSI = round(mean(SNSI), 3), .groups = "drop") %>%
  arrange(year, desc(mean_SNSI))

print(table1)

cat("\nOverall mean SNSI by cycle:\n")
snsi_final %>%
  group_by(year) %>%
  summarise(mean_SNSI = round(mean(SNSI), 3)) %>%
  print()

cat("\nNitrogen deficiency summary statistics (2023-24):\n")
snsi_23 <- snsi_final %>% filter(year == "2023-24")
cat("  Mean def_N:", round(mean(snsi_23$def_N), 3), "\n")
cat("  Median def_N:", round(median(snsi_23$def_N), 3), "\n")
cat("  Mean def_OC:", round(mean(snsi_23$def_OC), 3), "\n")
cat("  Mean def_K:", round(mean(snsi_23$def_K), 3), "\n")
cat("  Mean def_Zn:", round(mean(snsi_23$def_Zn), 3), "\n\n")

cat("Districts worsening 2023-24 to 2024-25:\n")
n_worsened <- sum(master_v3$direction == "Worsened", na.rm = TRUE)
cat("  ", n_worsened, "of", nrow(master_v3), "districts worsened\n\n")


# ===============================================================
# SECTION 4.2: PCA VALIDATION AND SNSI SENSITIVITY (TABLE 2)
# ===============================================================

cat("=== TABLE 2: PCA component loadings ===\n")

pca_input <- snsi_23 %>%
  select(def_N, def_P, def_K, def_OC, def_Zn) %>%
  scale()

pca_result <- prcomp(pca_input, center = TRUE, scale. = FALSE)

cat("Variance explained:\n")
print(round(summary(pca_result)$importance[2, 1:3] * 100, 1))

cat("\nLoadings (PC1-PC3):\n")
print(round(pca_result$rotation[, 1:3], 3))

# Validate PC1 against SNSI
snsi_23$PC1 <- pca_result$x[, 1]
pc1_cor <- cor(snsi_23$PC1, snsi_23$SNSI)
cat("\nPC1-SNSI correlation: r =", round(pc1_cor, 3), "\n")

val_model <- lm(SNSI ~ PC1 + pca_result$x[, 2], data = snsi_23)
cat("Validation regression R-squared:", round(summary(val_model)$r.squared, 3), "\n\n")

# --- Sensitivity analysis: equal vs PCA vs entropy weights ---
cat("=== SNSI Sensitivity Analysis ===\n")

pc1_loadings <- abs(pca_result$rotation[, 1])
pc1_weights  <- pc1_loadings / sum(pc1_loadings)
cat("PCA-derived weights:\n")
print(round(pc1_weights, 3))

cv_vals <- sapply(c("def_N", "def_P", "def_K", "def_OC", "def_Zn"),
                   function(v) sd(snsi_23[[v]]) / mean(snsi_23[[v]]))
entropy_weights <- cv_vals / sum(cv_vals)
cat("\nEntropy weights:\n")
print(round(entropy_weights, 3))

snsi_sens <- snsi_23 %>%
  mutate(
    SNSI_equal   = SNSI,
    SNSI_pca     = def_N * pc1_weights["def_N"]  + def_P * pc1_weights["def_P"] +
                   def_K * pc1_weights["def_K"]  + def_OC * pc1_weights["def_OC"] +
                   def_Zn * pc1_weights["def_Zn"],
    SNSI_entropy = def_N * entropy_weights["def_N"]  + def_P * entropy_weights["def_P"] +
                   def_K * entropy_weights["def_K"]  + def_OC * entropy_weights["def_OC"] +
                   def_Zn * entropy_weights["def_Zn"]
  )

cat("\nSpearman rank correlations between SNSI variants:\n")
print(round(cor(snsi_sens[, c("SNSI_equal", "SNSI_pca", "SNSI_entropy")],
                method = "spearman"), 3))

cat("\nComponent correlation matrix (def_N, def_P, def_K, def_OC, def_Zn):\n")
print(round(cor(snsi_23[, c("def_N", "def_P", "def_K", "def_OC", "def_Zn")]), 3))


# ===============================================================
# SECTION 4.3: SPATIAL STRUCTURE AND CLUSTERING
# ===============================================================

cat("\n=== Moran's I and cluster profile (loaded from data) ===\n")
# NOTE: Moran's I requires the spatial weights matrix (k=4 nearest
# neighbours) built from district centroids, which depends on a
# shapefile not included in this package due to size and
# licensing. Spatial test statistics are reported directly from
# the manuscript: Moran's I (SNSI) = 0.284, p = 0.002.
# See cluster_profiles.csv for the k-means cluster summary
# statistics used in Section 4.3.

print(cluster_profiles)


# ===============================================================
# SECTION 4.4: CORRELATES OF N_DOMINANCE (TABLE 3)
# ===============================================================

cat("\n=== TABLE 3: N_dominance regression (n=34) ===\n")

reg_ndom <- lm(N_dominance ~ soil_test_rate + irrig_share +
                 share_graduate + avg_age + fert_intensity_per_ha,
               data = master_v3)
print(summary(reg_ndom))


# ===============================================================
# SECTION 4.5: CROP SYSTEM COMPOSITION AND SNSI (TABLE 4)
# ===============================================================

cat("\n=== TABLE 4: SNSI regression, parsimonious model (n=31) ===\n")

# Three districts (Ahilyanagar, Chhatrapati Sambhajinagar,
# Dharashiv) have structural missing values for share_pulses
# and are automatically dropped by lm() via listwise deletion.

reg_snsi_base <- lm(SNSI ~ share_pulses + share_oilseeds +
                      N_dominance + soil_test_rate + avg_age,
                    data = master_v3)
print(summary(reg_snsi_base))
cat("n =", nobs(reg_snsi_base), "\n\n")

cat("=== Rainfall-controlled specification ===\n")
reg_snsi_rain <- lm(SNSI ~ share_pulses + share_oilseeds +
                      N_dominance + soil_test_rate +
                      avg_age + mean_rainfall,
                    data = master_v3)
print(summary(reg_snsi_rain))

# --- Partial correlation: pulse vs SNSI controlling rainfall ---
cat("\n=== Partial correlation: pulse share vs SNSI | rainfall ===\n")

pc_data <- master_v3 %>%
  select(SNSI, share_pulses, mean_rainfall) %>%
  filter(complete.cases(.))

resid_pulse <- residuals(lm(share_pulses ~ mean_rainfall, data = pc_data))
resid_snsi  <- residuals(lm(SNSI ~ mean_rainfall, data = pc_data))
partial_r   <- cor(resid_pulse, resid_snsi)

cat("Bivariate r (pulse, SNSI):",
    round(cor(pc_data$share_pulses, pc_data$SNSI), 3), "\n")
cat("Partial r (pulse, SNSI | rainfall):", round(partial_r, 3), "\n")
cat("Bivariate r (pulse share, rainfall):",
    round(cor(master_v3$share_pulses, master_v3$mean_rainfall,
              use = "complete.obs"), 3), "\n\n")


# ===============================================================
# SECTION 4.6: QUANTILE REGRESSION (TABLE 5)
# ===============================================================

cat("=== TABLE 5: Quantile regression with bootstrap CIs ===\n")

qr_data <- master_v3 %>%
  select(SNSI, share_pulses, share_oilseeds, N_dominance,
         soil_test_rate, avg_age, mean_rainfall) %>%
  filter(complete.cases(.))

cat("n =", nrow(qr_data), "(complete cases; Ratnagiri excluded due to\n")
cat("missing IMD rainfall data)\n\n")

taus <- c(0.25, 0.50, 0.75, 0.90)

qr_model <- rq(SNSI ~ share_pulses + share_oilseeds + N_dominance +
                 soil_test_rate + avg_age,
               tau = taus, data = qr_data)

cat("Quantile regression coefficients with bootstrap SE (1000 reps):\n")
print(summary(qr_model, se = "boot", R = 1000))

# Pseudo R-squared (Koenker-Machado)
pseudo_r2 <- sapply(taus, function(tau) {
  fit_full <- rq(SNSI ~ share_pulses + share_oilseeds + N_dominance +
                   soil_test_rate + avg_age, tau = tau, data = qr_data)
  fit_null <- rq(SNSI ~ 1, tau = tau, data = qr_data)
  rho <- function(u, t) u * (t - (u < 0))
  1 - sum(rho(residuals(fit_full), tau)) / sum(rho(residuals(fit_null), tau))
})
names(pseudo_r2) <- paste0("Q", c(25, 50, 75, 90))
cat("\nPseudo R-squared by quantile:\n")
print(round(pseudo_r2, 3))

cat("\n=== Quantile regression with rainfall control ===\n")
qr_rain <- rq(SNSI ~ share_pulses + share_oilseeds + N_dominance +
                soil_test_rate + avg_age + mean_rainfall,
              tau = taus, data = qr_data)
print(summary(qr_rain, se = "boot", R = 1000))

# Wald test of slope equality across quantiles
cat("\n=== Wald test of slope equality across quantiles ===\n")
anova_qr <- anova(qr_model)
print(anova_qr)


# ===============================================================
# SECTION 4.7: FARMER AGE, EDUCATION, AND NPK IMBALANCE
# ===============================================================

cat("\n=== Age and education direct effects on SNSI ===\n")

reg_age_direct <- lm(SNSI ~ avg_age + share_pulses + share_oilseeds +
                       N_dominance, data = master_v3)
print(summary(reg_age_direct))

cat("\n=== Education-stress association ===\n")
reg_edu_direct <- lm(SNSI ~ share_graduate + share_pulses +
                       N_dominance, data = master_v3)
print(summary(reg_edu_direct))

cat("\n=== Supporting data: irrigation/horticultural share, ===\n")
cat("=== named commercially intensive districts            ===\n")
named_districts <- c("Pune", "Nashik", "Kolhapur", "Sangli")
master_v3 %>%
  filter(district_name %in% named_districts) %>%
  summarise(
    mean_irrig = round(mean(irrig_share, na.rm = TRUE), 2),
    mean_sugarcane_oilseed = round(mean(share_sugarcane, na.rm = TRUE) +
                                    mean(share_oilseeds, na.rm = TRUE), 2)
  ) %>%
  print()

cat("State means for comparison:\n")
master_v3 %>%
  summarise(
    state_mean_irrig = round(mean(irrig_share, na.rm = TRUE), 2),
    state_mean_sugarcane_oilseed = round(mean(share_sugarcane, na.rm = TRUE) +
                                          mean(share_oilseeds, na.rm = TRUE), 2)
  ) %>%
  print()


# ===============================================================
# SECTION 5.3: SOIL TESTING NULL RESULT (BIVARIATE CHECKS)
# ===============================================================

cat("\n=== Soil testing bivariate null results ===\n")

cat("SNSI ~ soil_test_rate:\n")
print(summary(lm(SNSI ~ soil_test_rate, data = master_v3)))

cat("\nN_dominance ~ soil_test_rate:\n")
print(summary(lm(N_dominance ~ soil_test_rate, data = master_v3)))


# ===============================================================
# SUPPLEMENTARY: VILLAGE COVERAGE TABLE A1
# ===============================================================
# Village coverage statistics (Table A1) require the raw village-
# level SHC counts and Census 2011 village totals, which are
# tabulated separately and not reconstructed in this script.
# See manuscript Supplementary Table A1 for full district-level
# coverage figures.


cat("\n================================================\n")
cat("Replication script complete.\n")
cat("All tables and statistics above correspond to those\n")
cat("reported in the manuscript Sections 4.1 to 4.7 and 5.3.\n")
cat("================================================\n")
