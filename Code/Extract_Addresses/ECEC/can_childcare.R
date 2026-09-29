library(tidyverse)
library(readxl)

getwd() # this should be the geographic_ineq folder 
base_path <- file.path("1_services", "ecec")

isced_mapping <- c(
  "ISCED11_0"           = "Early childhood education",
  "ISCED11_01"          = "Early childhood educational development",
  "ISCED11_02"          = "Pre-primary education"
)

### Quebec -------------------------------------

quebec_meta <- read.csv(file.path(base_path, "data", "raw", "repertoire-installation.csv"))

quebec <- quebec_meta %>%
  # rename columns of interest
  rename(
    name = NOM,
    sector = TYPE,
    students_LT2 = PLACE_TOTAL_POUPON,
    students = PLACE_TOTAL
  )%>%
  mutate(
    CODE_POSTAL_COMPO = gsub(" ", "-", CODE_POSTAL_COMPO),
    sector = case_when(
      sector == "CPE" ~ "Public",
      sector == "GARD" ~ "Private",
    )
  )%>%
  select(-CODE_REGION_COMPO, -SUBV, -telephone1, -TELECOPIEUR1, -INTERNET)

# creating columns (i.e. isced, isced_detailed, level_en, level_or, id and street_address)
quebec$isced <- "ISCED11_0"
quebec$isced_detailed <- dplyr::case_when(
  quebec$students_LT2 == 0 ~ "ISCED11_02",
  TRUE                 ~ "ISCED11_0"
)
quebec$level_en <- isced_mapping[quebec$isced_detailed]
quebec$level_or <- "-"
quebec$id <- paste0("CA24_", seq_len(nrow(quebec)))
quebec$street_address <- paste0(quebec$ADRESSE, ", ", quebec$NOM_MUN_COMPO, ", ", quebec$PROVINCE, " ", quebec$CODE_POSTAL_COMPO)

# dropping unneeded columns and uploading to the output folder
quebec <- quebec %>% select(-NOM_MUN_COMPO, -CODE_POSTAL_COMPO, -PROVINCE, -REGION, -ADRESSE)
write.csv(quebec, file=paste0(file.path(base_path, "data", "output", "CA24.csv")), row.names=FALSE)


### New Brunswick -------------------------------------

new_brunswick_meta <- read.csv(file.path(base_path, "data", "raw", "Licensed_Early_Learning_and_Childcare_Facilities.csv"))

new_brunswick <- new_brunswick_meta %>%
  # rename columns of interest
  rename(
    id = License.Number,
    name = Facility.Name,
    students_LT2 = Max.Number.of.Infants,
    students_2T5 = Max.Number.of.Preschool.Aged.Children,
    students = Max.Number.of.Children
  )%>%
  mutate(
    Facility.Address.3 = gsub(" ", "-", Facility.Address.3),
  )

new_brunswick$isced <- "ISCED11_0"
new_brunswick$isced_detailed <- dplyr::case_when(
  new_brunswick$students_LT2 == 0 ~ "ISCED11_02",
  new_brunswick$students_2T5 == 0     ~ "ISCED11_01",
  TRUE                 ~ "ISCED11_0"
)

# creating new columns (i.e. level_en, level_or and street_address)
new_brunswick$level_en <- isced_mapping[new_brunswick$isced_detailed]
new_brunswick$level_or <- "-"
new_brunswick$sector <- "-"
new_brunswick$street_address <- paste0(new_brunswick$Facility.Address.1, ", ", new_brunswick$Facility.Address.2, " ",
                                       new_brunswick$Facility.Address.3)

# dropping unwanted columns
new_brunswick <- new_brunswick %>% select(-Facility.Address.1, -Facility.Address.2, -Facility.Address.3, -Region, -District,
                                          -Language.of.Service, -Operator.Id, -Designated.Facility, -Facility.Type, -Max.Number.of.School.Age.Children)
write.csv(new_brunswick,file=paste0(file.path(base_path, "data", "output", "CA13.csv")), row.names=FALSE)