

clear all 
cd "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Robustness check"
set scheme s2color 
import delimited "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Robustness check\aggregated_data.csv"
save temporal, replace
import delimited "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Robustness check\extracted_robustness.csv", clear

merge 1:1 tl3_id using temporal
drop if _merge == 2
replace tot_pop_2005 = tot_pop_2005_agg if _merge == 3
replace tot_pop_2019 = tot_pop_2019_agg if _merge == 3
replace tot_pop_2020 = tot_pop_2020_agg if _merge == 3
replace tot_pop_2022 = tot_pop_2022_agg if _merge == 3
replace pop_y0_4_2019 = pop_y0_4_2019_agg if _merge == 3
replace pop_y5_9_2019 = pop_y5_9_2019_agg if _merge == 3
replace unem_ra_15_64_2019 = unem_ra_15_64_2019_agg if _merge == 3
replace surf_2022 = surf_2022_agg if _merge == 3
replace gdp_tot_real_ppp_2019 = gdp_tot_real_ppp_2019_agg if _merge == 3
replace gdp_tot_real_ppp_2005 = gdp_tot_real_ppp_2005_agg if _merge == 3
replace gdp_tot_real_ppp_2020 = gdp_tot_real_ppp_2020_agg if _merge == 3
drop tot_pop_2005_agg tot_pop_2019_agg tot_pop_2022_agg surf_2022_agg pop_y0_4_2019_agg pop_y5_9_2019_agg gdp_tot_real_ppp_2019_agg gdp_tot_real_ppp_2005_agg gdp_tot_real_ppp_2020_agg tot_pop_2020_agg unem_ra_15_64_2019_agg
replace pop_den_2022 = tot_pop_2022 / surf_2022 if _merge == 3
replace gdp_pc_real_ppp_2005 = gdp_tot_real_ppp_2005 / tot_pop_2005 if _merge == 3
replace gdp_pc_real_ppp_2019 = gdp_tot_real_ppp_2019 / tot_pop_2019 if _merge == 3
replace gdp_pc_real_ppp_2020 = gdp_tot_real_ppp_2020 / tot_pop_2020 if _merge == 3
drop if metro_code_agg != ""

foreach var of varlist _all {
    local newname = upper("`var'")
    rename `var' `newname'
}

rename TL3_ID tl3_id 
rename TYPOLOGY_ACCESS_CITIES typology_access_cities
rename PES_DRIVING_15 pes_driving_15
rename CARE_WALKING_15 care_walking_15
rename PRIM_WALKING_15 prim_walking_15

**************************************************************
**** GENERATING USEFUL VARIABLES AND KEEPING RELEVANT OBS.****
**************************************************************


** Generating useful variables that will be used in the analysis
gen lnPOP_DEN_2022 = ln(POP_DEN_2022)
gen lnGDP_PC_REAL_PPP_2019 = ln(GDP_PC_REAL_PPP_2019)
gen lnGDP_PC_REAL_PPP_2005 = ln(GDP_PC_REAL_PPP_2005)
gen lnGDP_PC_REAL_PPP_2020 = ln(GDP_PC_REAL_PPP_2020)
gen lnTOT_POP_2022 = ln(TOT_POP_2022)
gen lnTOT_POP_2005 = ln(TOT_POP_2005)
gen GDPpcgrowthannual = ((lnGDP_PC_REAL_PPP_2019 - lnGDP_PC_REAL_PPP_2005) / 15)*100 //Annual GDP per capita growth
gen GDPpcgrowth = ((GDP_PC_REAL_PPP_2019 - GDP_PC_REAL_PPP_2005) / GDP_PC_REAL_PPP_2005)*100 // GDP per capita growth
gen populationgrowthannual = ((lnTOT_POP_2022 - lnTOT_POP_2005) / 17)*100 //Annual population growth
gen populationgrowth = ((TOT_POP_2022 - TOT_POP_2005) / TOT_POP_2005)*100 // population growth
gen popshare5_9 = (POP_Y5_9_2019 / TOT_POP_2019) * 100
gen popshare0_4 = (POP_Y0_4_2019 / TOT_POP_2019) * 100
encode ISO3, gen(country)

** Generating categories based on access to cities typologies

gen metro_5 = "Metropolitan Large" if typology_access_cities == "MR-L"
replace metro_5 = "Metropolitan Medium" if typology_access_cities == "MR-M"
replace metro_5 = "Non-metropolitan access to medium city" if typology_access_cities == "NMR-M"
replace metro_5 = "Non-metropolitan access to small city" if typology_access_cities == "NMR-S" 
replace metro_5 = "Non-metropolitan remote" if typology_access_cities == "NMR-R" 
encode metro_5, gen (metro_5_num)

gen metro_4 = "Metropolitan" if typology_access_cities == "MR-L" | typology_access_cities == "MR-M" 
replace metro_4 = "Non-metropolitan access to medium city" if typology_access_cities == "NMR-M"
replace metro_4 = "Non-metropolitan access to small city" if typology_access_cities == "NMR-S" 
replace metro_4 = "Non-metropolitan remote" if typology_access_cities == "NMR-R" 

gen metro_3 = "Metropolitan" if typology_access_cities == "MR-L" | typology_access_cities == "MR-M" 
replace metro_3 = "Non-metropolitan access to metro" if typology_access_cities == "NMR-M" | typology_access_cities == "NMR-S"
replace metro_3 = "Non-metropolitan remote" if typology_access_cities == "NMR-R" 

gen metro_2 = "Metropolitan" if typology_access_cities == "MR-L" | typology_access_cities == "MR-M" 
replace metro_2 = "Non-metropolitan" if typology_access_cities == "NMR-M" | typology_access_cities == "NMR-S" | typology_access_cities == "NMR-R" 
encode metro_2, gen (metro_2_num)


** Generating weights for regressions

egen number_regions = count(tl3_id), by(ISO3) // In the regressions, the observations are weighted by the inverse of the number of regions in each country.

** Generating share of population that can reach a service in under 15 minutes by motor vehicule (PES) or by foot (primary schools / ECEC)

gen pes_driving_15_100 = pes_driving_15*100
gen prim_walking_15_100 = prim_walking_15*100
gen care_walking_15_100 = care_walking_15*100

** Set to missing those regions for which we do not have data (hence population share is 0%)

replace pes_driving_15_100 =. if tl3_id == "FI200" | tl3_id == "SI214" | tl3_id == "ES531" | tl3_id == "FRY5"
replace prim_walking_15_100 =. if tl3_id == "PT200" | tl3_id == "PT300" | tl3_id == "ITH10" | tl3_id == "ITH20" | tl3_id == "ITC20"
replace care_walking_15_100 =. if tl3_id == "ITH10" | tl3_id == "ITH20" | tl3_id == "ITC20"


**************************************************************
******************* FIGURES DESCRIPTIVES *********************
**************************************************************

************** Figure GDP per capita - PES


// List of y-variables to loop over
local yvariables "pes_driving_15_100" 

// List of x-variables to loop over
local xvariables "lnGDP_PC_REAL_PPP_2019" 

// Corresponding x-axis titles
local xtitles `" "GDP per capita in 2019 (logarithmic scale)"'

// Specify the six ISO3 country codes
local countries "FRA DEU NLD ESP SWE CHE"

local n 1
foreach x in `xvariables' {
    local xtitle : word `n' of `xtitles' // get the corresponding x-axis title

    foreach y in `yvariables' {
        local income_all_
   
        
        // Iterate over each country, calculate the regression coefficient
        foreach c in `countries' {
            
            // Assign country names based on ISO3 codes
            local countryName
            if "`c'" == "ESP" local countryName "Spain"
            else if "`c'" == "SWE" local countryName "Sweden"
            else if "`c'" == "FRA" local countryName "France"
            else if "`c'" == "CHE" local countryName "Switzerland"
            else if "`c'" == "DEU" local countryName "Germany"
            else if "`c'" == "NLD" local countryName "Netherlands"
            
            // Check if there are non-missing values for the current X variable for the country
            count if `x' != . & `y' != . & ISO3 == "`c'"
            if r(N) > 1 {
                
                corr `y' `x' if ISO3 == "`c'"
                local corr : di %5.3g r(rho)
                
                qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(0(20)100, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
                
                local income_all_ `income_all_' graph`c'
                di "`income_all_'"
            }
        } 

        // Combine plots for each pair of x and y variables
        grc1leg `income_all_',  imargin(1 1 1 1) ycommon graphregion(color(white)) ///
            b2title("`xtitle'", size(medsmall)) ///
            l1title("Percentage of people (%)", size(medsmall)) ring(2)

        // Export graph for each pair of x and y variables
        graph export "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Figures\Figures characteristics\FigGDPpercapita_`x'_`y'.svg", replace 

    }
    
    local ++n // move to the next title
}



************************ Figure GDP per capita Annex


// List of y-variables to loop over
local yvariables "prim_walking_15_100 care_walking_15_100" 

// Corresponding y-axis titles
local ytitles `" "Percentage of people (%)" "Percentage of people (%)""'

// List of x-variables to loop over
local xvariables "lnGDP_PC_REAL_PPP_2019" 

// Corresponding x-axis titles
local xtitles `""GDP per capita in 2019 (logarithmic scale)""'

// Specify the six ISO3 country codes
local countries "BEL FIN FRA IRL NLD ESP"

local n 1
foreach x in `xvariables' {
    local xtitle : word `n' of `xtitles' // get the corresponding x-axis title
    
	
    foreach y in `yvariables' {
		local ytitle : word `n' of `ytitles' // get the corresponding x-axis title
        local income_all_
   
        
        // Iterate over each country, calculate the regression coefficient
        foreach c in `countries' {
            
            // Assign country names based on ISO3 codes
            local countryName
            if "`c'" == "BEL" local countryName "Belgium"
            else if "`c'" == "FRA" local countryName "France"
            else if "`c'" == "FIN" local countryName "Finland"
            else if "`c'" == "IRL" local countryName "Ireland"
            else if "`c'" == "NLD" local countryName "Netherlands"
            else if "`c'" == "ESP" local countryName "Spain"
            
            // Check if there are non-missing values for the current X variable for the country
            count if `x' != . & `y' != . & ISO3 == "`c'"
            if r(N) > 1 {
                
                corr `y' `x' if ISO3 == "`c'"
                local corr : di %5.3g r(rho)
                
                qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
                
                local income_all_ `income_all_' graph`c'
                di "`income_all_'"
            }
        } 

        // Combine plots for each pair of x and y variables
        grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
            b2title("`xtitle'", size(medsmall)) ///
            l1title("`ytitle'", size(medsmall)) ring(2)

        // Export graph for each pair of x and y variables
        graph export "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Figures\Figures characteristics\AGDPpercapita_`x'_`y'.svg", replace
		
		 local ++n // move to the next title
    }
    
    local ++n // move to the next title
}


*************************** Figure GDP per capita growth annex

// List of y-variables to loop over
local yvariables "pes_driving_15_100" 

// List of x-variables to loop over
local xvariables "GDPpcgrowthannual" 

// Corresponding x-axis titles
local xtitles `" "Annual GDP per capita growth 2005-2019 (%)"'

// Specify the six ISO3 country codes
local countries "FRA DEU ITA NLD ESP SWE"

local n 1
foreach x in `xvariables' {
    local xtitle : word `n' of `xtitles' // get the corresponding x-axis title

    foreach y in `yvariables' {
        local income_all_
   
        
        // Iterate over each country, calculate the regression coefficient
        foreach c in `countries' {
            
            // Assign country names based on ISO3 codes
            local countryName
            if "`c'" == "ESP" local countryName "Spain"
            else if "`c'" == "SWE" local countryName "Sweden"
            else if "`c'" == "FRA" local countryName "France"
            else if "`c'" == "ITA" local countryName "Italy"
            else if "`c'" == "DEU" local countryName "Germany"
            else if "`c'" == "NLD" local countryName "Netherlands"
            
            // Check if there are non-missing values for the current X variable for the country
            count if `x' != . & `y' != . & ISO3 == "`c'"
            if r(N) > 1 {
                
                corr `y' `x' if ISO3 == "`c'"
                local corr : di %5.3g r(rho)
                
                qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
                
                local income_all_ `income_all_' graph`c'
                di "`income_all_'"
            }
        } 

        // Combine plots for each pair of x and y variables
        grc1leg `income_all_',  imargin(1 1 1 1) ycommon graphregion(color(white)) ///
            b2title("`xtitle'", size(medsmall)) ///
            l1title("Percentage of people (%)", size(medsmall)) ring(2)

        // Export graph for each pair of x and y variables
        graph export "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Figures\Figures characteristics\AGDPpcgrowth_`x'_`y'.svg", replace
    }
    
    local ++n // move to the next title
}


// List of y-variables to loop over
local yvariables "prim_walking_15_100 care_walking_15_100" 

// Corresponding y-axis titles
local ytitles `" "Percentage of people (%)" "Percentage of people (%)""'

// List of x-variables to loop over
local xvariables "GDPpcgrowthannual" 

// Corresponding x-axis titles
local xtitles `" "Annual GDP per capita growth 2005-2019 (%)"'

// Specify the six ISO3 country codes
local countries "BEL FIN FRA IRL NLD ESP"

local n 1
foreach x in `xvariables' {
    local xtitle : word `n' of `xtitles' // get the corresponding x-axis title
    
	
    foreach y in `yvariables' {
		local ytitle : word `n' of `ytitles' // get the corresponding x-axis title
        local income_all_
   
        
        // Iterate over each country, calculate the regression coefficient
        foreach c in `countries' {
            
            // Assign country names based on ISO3 codes
            local countryName
            if "`c'" == "BEL" local countryName "Belgium"
            else if "`c'" == "FRA" local countryName "France"
            else if "`c'" == "FIN" local countryName "Finland"
            else if "`c'" == "IRL" local countryName "Ireland"
            else if "`c'" == "NLD" local countryName "Netherlands"
            else if "`c'" == "ESP" local countryName "Spain"
            
            // Check if there are non-missing values for the current X variable for the country
            count if `x' != . & `y' != . & ISO3 == "`c'"
            if r(N) > 1 {
                
                corr `y' `x' if ISO3 == "`c'"
                local corr : di %5.3g r(rho)
                
                qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
                
                local income_all_ `income_all_' graph`c'
                di "`income_all_'"
            }
        } 

        // Combine plots for each pair of x and y variables
        grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
            b2title("`xtitle'", size(medsmall)) ///
            l1title("`ytitle'", size(medsmall)) ring(2)

        // Export graph for each pair of x and y variables
        graph export "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Figures\Figures characteristics\AGDPpcgrowth_`x'_`y'.svg", replace
		
		 local ++n // move to the next title
    }
    
    local ++n // move to the next title
}


************************************ Figure unemployment rate

// List of y-variables to loop over
local yvariables "pes_driving_15_100" 
local ytitles `" "Percentage of people (%)""'

// List of x-variables to loop over
local xvariables "UNEM_RA_15_64_2019" 

// Corresponding x-axis titles
local xtitles `" "Unemployment rate in 2019 (%)"'

// Specify the six ISO3 country codes
local countries "FRA DEU HUN ESP SWE CHE"

local n 1
foreach x in `xvariables' {
    local xtitle : word `n' of `xtitles' // get the corresponding x-axis title

    foreach y in `yvariables' {
		local ytitle : word `n' of `ytitles' // get the corresponding x-axis title
        local income_all_
   
        
        // Iterate over each country, calculate the regression coefficient
        foreach c in `countries' {
            
            // Assign country names based on ISO3 codes
            local countryName
            if "`c'" == "ESP" local countryName "Spain"
            else if "`c'" == "SWE" local countryName "Sweden"
            else if "`c'" == "FRA" local countryName "France"
            else if "`c'" == "HUN" local countryName "Hungary"
            else if "`c'" == "DEU" local countryName "Germany"
            else if "`c'" == "CHE" local countryName "Switzerland"
            
            // Check if there are non-missing values for the current X variable for the country
            count if `x' != . & `y' != . & ISO3 == "`c'"
            if r(N) > 1 {
                
                corr `y' `x' if ISO3 == "`c'"
                local corr : di %5.3g r(rho)
                
                qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
                
                local income_all_ `income_all_' graph`c'
                di "`income_all_'"
            }
        } 

        // Combine plots for each pair of x and y variables
        grc1leg `income_all_',  imargin(1 1 1 1) ycommon graphregion(color(white)) ///
            b2title("`xtitle'", size(medsmall)) ///
            l1title("`ytitle'", size(medsmall)) ring(2)
        // Export graph for each pair of x and y variables
        graph export "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Figures\Figures characteristics\FigUnemployment_`x'_`y'.svg", replace
		
		 local ++n // move to the next title
    }
    
    local ++n // move to the next title
}


**************************************  Figure kidshare

** PRIM

// List of y-variables to loop over
local yvariables "prim_walking_15_100"

// Corresponding y-axis titles
local ytitles `" "Percentage of people (%)""'

// List of x-variables to loop over
local xvariables "popshare5_9"

// Corresponding x-axis titles
local xtitles `" "Share of children aged 5 to 9 (%)" "'


// Specify the six ISO3 country codes
local countries "BEL FIN FRA IRL NLD ESP"

local n 1
foreach x in `xvariables' {
    local xtitle : word `n' of `xtitles' // get the corresponding x-axis title
    
	
    foreach y in `yvariables' {
		local ytitle : word `n' of `ytitles' // get the corresponding x-axis title
        local income_all_
   
        
        // Iterate over each country, calculate the regression coefficient
        foreach c in `countries' {
            
            // Assign country names based on ISO3 codes
          local countryName
            if "`c'" == "BEL" local countryName "Belgium"
            else if "`c'" == "FRA" local countryName "France"
            else if "`c'" == "FIN" local countryName "Finland"
            else if "`c'" == "IRL" local countryName "Ireland"
            else if "`c'" == "ESP" local countryName "Spain"
            else if "`c'" == "NLD" local countryName "Netherlands"
            
            // Check if there are non-missing values for the current X variable for the country
            count if `x' != . & `y' != . & ISO3 == "`c'"
            if r(N) > 1 {
                
                corr `y' `x' if ISO3 == "`c'"
                local corr : di %5.3g r(rho)
                
                     
            if "`c'" == "BEL" | "`c'" == "FIN" | "`c'" == "IRL"| "`c'" == "ESP" | "`c'" == "NLD"  qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
              
				
			else if "`c'" == "FRA"	qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", range (3 10) lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
			
                
                local income_all_ `income_all_' graph`c'
                di "`income_all_'"
              }
        } 
        // Combine plots for each pair of x and y variables
        grc1leg `income_all_', imargin(1 1 1 1) ycommon graphregion(color(white)) ///
        b2title("`xtitle'", size(medsmall)) ///
        l1title("`ytitle'", size(medsmall)) ring(2)

        // Export graph for each pair of x and y variables
        graph export "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Figures\Figures characteristics\FigKidshare_`x'_`y'.svg", replace
		
		 local ++n // move to the next title
    }
    
    local ++n // move to the next title
}

** CARE

// List of y-variables to loop over
local yvariables "care_walking_15_100"

// Corresponding y-axis titles
local ytitles `""Percentage of people (%)""'

// List of x-variables to loop over
local xvariables "popshare0_4"

// Corresponding x-axis titles
local xtitles `" "Share of children aged 0 to 4 (%)" "'


// Specify the six ISO3 country codes
local countries "BEL FIN FRA IRL ESP NLD"

local n 1
foreach x in `xvariables' {
    local xtitle : word `n' of `xtitles' // get the corresponding x-axis title
    
	
    foreach y in `yvariables' {
		local ytitle : word `n' of `ytitles' // get the corresponding x-axis title
        local income_all_
   
        
        // Iterate over each country, calculate the regression coefficient
        foreach c in `countries' {
            
            // Assign country names based on ISO3 codes
           local countryName
            if "`c'" == "BEL" local countryName "Belgium"
            else if "`c'" == "FRA" local countryName "France"
            else if "`c'" == "FIN" local countryName "Finland"
            else if "`c'" == "IRL" local countryName "Ireland"
            else if "`c'" == "ESP" local countryName "Spain"
            else if "`c'" == "NLD" local countryName "Netherlands"
            
            // Check if there are non-missing values for the current X variable for the country
            count if `x' != . & `y' != . & ISO3 == "`c'"
            if r(N) > 1 {
                
                corr `y' `x' if ISO3 == "`c'"
                local corr : di %5.3g r(rho)
                
            if "`c'" == "BEL" | "`c'" == "FIN" | "`c'" == "IRL"| "`c'" == "ITA" | "`c'" == "ESP"  qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
				
			else if "`c'" == "FRA"	qui twoway (scatter `y' `x' if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
                    (scatter `y' `x' if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
                    ylabel(, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
                    legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
                    || lfit `y' `x' if ISO3 == "`c'", range (3 10) lcolor(red%75) title("`countryName'", color(black) size (medsmall)) ///
                    subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
			
			local income_all_ `income_all_' graph`c'
                di "`income_all_'"
			
              }
        } 
        // Combine plots for each pair of x and y variables
        grc1leg `income_all_', imargin(1 1 1 1) ycommon graphregion(color(white)) ///
        b2title("`xtitle'", size(medsmall)) ///
        l1title("`ytitle'", size(medsmall)) ring(2)
		
        // Export graph for each pair of x and y variables
        graph export "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\Database with variables - STATA\Figures\Figures characteristics\FigKidshare2_`x'_`y'.svg", replace
		
		 local ++n // move to the next title
    }
    
    local ++n // move to the next title
}


**************************************************************
******************** REGRESSIONS *****************************
**************************************************************


** PAPER REGRESSIONS

reg pes_driving_15_100 UNEM_RA_15_64_2019 i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) replace
reg pes_driving_15_100 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg pes_driving_15_100 lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg pes_driving_15_100 UNEM_RA_15_64_2019 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 popshare5_9 i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 popshare5_9 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 


** ROBUSTNESS CLUSTER  

reg pes_driving_15_100 UNEM_RA_15_64_2019 i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) replace
reg pes_driving_15_100 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg pes_driving_15_100 lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg pes_driving_15_100 UNEM_RA_15_64_2019 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 popshare5_9 i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_15_100 popshare5_9 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], vce(cluster country)
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country)  

** ROBUSTNESS THRESHOLD 30 MINS

reg pes_driving_30_100 UNEM_RA_15_64_2019 i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) replace
reg pes_driving_30_100 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg pes_driving_30_100 lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg pes_driving_30_100 UNEM_RA_15_64_2019 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_30_100 popshare5_9 i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_30_100 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_30_100 lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_walking_30_100 popshare5_9 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country)  

** ROBUSTNESS MEDIAN TRAVELTIMES

reg PES_traveltime_driving_median UNEM_RA_15_64_2019 i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) replace
reg PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg PES_traveltime_driving_median lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg PES_traveltime_driving_median UNEM_RA_15_64_2019 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_traveltime_walking_median popshare5_9 i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_traveltime_walking_median lnTOT_POP_2022 populationgrowthannual i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country) 
reg prim_traveltime_walking_median popshare5_9 lnGDP_PC_REAL_PPP_2019 GDPpcgrowthannual lnTOT_POP_2022 populationgrowthannual lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
outreg2 using results.doc, stats (coef se) bdec(3) rdec(3) append ctitle(OLS) addtext (Country FE, YES) addstat(Adjusted R-squared, e(r2_a)) nocons drop(i.country)  

break code









//// OLD CODE PIECES THAT COULD BE USEFUL IN THE FUTURE

keep if prim_traveltime_walking_bottom20 !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_8 == 1


*************** ALL regions together ******************

// List of variables to loop over
local variables "prim_traveltime_walking_bottom20 prim_traveltime_walking_median prim_traveltime_walking_top20" 
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)

foreach v in `variables' {
    local income_all_
    
    // Iterate over each country, calculate the regression coefficient
    foreach c in `countries' {
        
        corr `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'"
        local corr : di %5.3g r(rho)
        
        qui twoway (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
            (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
            ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
            legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
            || lfit `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) ///
            subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
        
        local income_all_ `income_all_' graph`c'
        di "`income_all_'"
    } 

    // Combine plots
    grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
        b2title("GDP per capita 2019 in logarithmic scale (international $)", size(medium)) ///
        l1title("Walking time to primary schools", size(medium)) ring(2)

    // Export graph
    graph export "income_all_`v'.png", replace
}




*************** Metro  ******************

// List of variables to loop over
local variables "prim_traveltime_walking_bottom20 prim_traveltime_walking_median prim_traveltime_walking_top20" 

foreach v in `variables' {
    local income_all_
    
    // Get the list of countries
    levelsof ISO3, local(countries)
    
    // Iterate over each country, calculate the regression coefficient
    foreach c in `countries' {
        
        corr `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Metropolitan"
        local corr : di %5.3g r(rho)
        
        qui twoway (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large" & ISO3 == "`c'", mcolor(red%50)) ///
            (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium" & ISO3 == "`c'", mcolor(navy%50)), ///
            ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
            legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) bgcolor(white) ///
            || lfit `v' lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" & ISO3 == "`c'", ///
            title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
        
        local income_all_ `income_all_' graph`c'
        di "`income_all_'"
    } 

    // Combine plots
    grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
        b2title("GDP per capita 2019 in logarithmic scale (international $)", size(medium)) ///
        l1title("Walking time to primary schools", size(medium)) ring(2)

    // Export graph
    graph export "income_metro_`v'.png", replace
}



*************** Non-metro  ******************


// List of variables to loop over
local variables "prim_traveltime_walking_bottom20 prim_traveltime_walking_median prim_traveltime_walking_top20" 

foreach v in `variables' {
    local income_all_
    
    // Get the list of countries
    levelsof ISO3, local(countries)
    
    // Iterate over each country, calculate the regression coefficient
    foreach c in `countries' {
        
        corr `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Non-metropolitan"
        local corr : di %5.3g r(rho)
        
        qui twoway (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro" & ISO3 == "`c'", mcolor(red%50)) ///
            (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote" & ISO3 == "`c'", mcolor(navy%50)), ///
            ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
            legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) bgcolor(white) ///
            || lfit `v' lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" & ISO3 == "`c'", ///
            title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
        
        local income_all_ `income_all_' graph`c'
        di "`income_all_'"
    } 

    // Combine plots
    grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
        b2title("GDP per capita 2019 (2015 international $)", size(medium)) ///
        l1title("Walking time to primary schools", size(medium)) ring(2)

    // Export graph
    graph export "income_nonmetro_`v'.png".png", replace
}




////////////////// Income travel times ECEC //////////////////////


keep if care_traveltime_walking_bottom20 !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_8 == 1


*************** ALL regions together ******************

// List of variables to loop over
local variables "care_traveltime_walking_bottom20 care_traveltime_walking_median care_traveltime_walking_top20" 
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)

foreach v in `variables' {
    local income_all_
    
    // Iterate over each country, calculate the regression coefficient
    foreach c in `countries' {
        
        corr `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'"
        local corr : di %5.3g r(rho)
        
        qui twoway (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) ///
            (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ///
            ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
            legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) ///
            || lfit `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) ///
            subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
        
        local income_all_ `income_all_' graph`c'
        di "`income_all_'"
    } 

    // Combine plots
    grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
        b2title("GDP per capita 2019 in logarithmic scale (international $)", size(medium)) ///
        l1title("Walking time to ECEC", size(medium)) ring(2)

    // Export graph
    graph export "income_all_`v'.png", replace
}




*************** Metro  ******************

// List of variables to loop over
local variables "care_traveltime_walking_bottom20 care_traveltime_walking_median care_traveltime_walking_top20"  

foreach v in `variables' {
    local income_all_
    
    // Get the list of countries
    levelsof ISO3, local(countries)
    
    // Iterate over each country, calculate the regression coefficient
    foreach c in `countries' {
        
        corr `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Metropolitan"
        local corr : di %5.3g r(rho)
        
        qui twoway (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large" & ISO3 == "`c'", mcolor(red%50)) ///
            (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium" & ISO3 == "`c'", mcolor(navy%50)), ///
            ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
            legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) bgcolor(white) ///
            || lfit `v' lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" & ISO3 == "`c'", ///
            title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
        
        local income_all_ `income_all_' graph`c'
        di "`income_all_'"
    } 

    // Combine plots
    grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
        b2title("GDP per capita 2019 in logarithmic scale (international $)", size(medium)) ///
        l1title("Walking time to ECEC", size(medium)) ring(2)

    // Export graph
    graph export "income_metro_`v'.png", replace
}



*************** Non-metro  ******************


// List of variables to loop over
local variables "care_traveltime_walking_bottom20 care_traveltime_walking_median care_traveltime_walking_top20"  

foreach v in `variables' {
    local income_all_
    
    // Get the list of countries
    levelsof ISO3, local(countries)
    
    // Iterate over each country, calculate the regression coefficient
    foreach c in `countries' {
        
        corr `v' lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Non-metropolitan"
        local corr : di %5.3g r(rho)
        
        qui twoway (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro" & ISO3 == "`c'", mcolor(red%50)) ///
            (scatter `v' lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote" & ISO3 == "`c'", mcolor(navy%50)), ///
            ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") ///
            legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) bgcolor(white) ///
            || lfit `v' lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" & ISO3 == "`c'", ///
            title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
        
        local income_all_ `income_all_' graph`c'
        di "`income_all_'"
    } 

    // Combine plots
    grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) ///
        b2title("GDP per capita 2019 (2015 international $)", size(medium)) ///
        l1title("Walking time to ECEC", size(medium)) ring(2)

    // Export graph
    graph export "income_nonmetro_`v'.png".png", replace
}





























////////////////// Income travel times EC //////////////////////


keep if care_traveltime_walking_median !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_8 == 1


*******************
**** Bottom 20 ****
*******************

******* ALL *******

/
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) || lfit care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("GDP per capita 2019 in logarithmic scale (international $)", size(medium)) l1title("Travel times to ECEC - Bottom 20%", size(medium)) ring(2)
*/

graph export mygraph.png, replace


******* METRO / NON-METRO *******

/
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Metropolitan"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large" & ISO3 == "`c'", mcolor(red%50)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium" & ISO3 == "`c'", mcolor(navy%50) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) bgcolor(white) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" & ISO3 == "`c'",title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("GDP per capita 2019 (2015 international $)", size(medium)) l1title("Travel times to PES", size(medium)) ring(2)
*/

/*
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Non-metropolitan"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro" & ISO3 == "`c'", mcolor(red%50)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote" & ISO3 == "`c'", mcolor(navy%50) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) bgcolor(white) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" & ISO3 == "`c'",title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("GDP per capita 2019 (2015 international $)", size(medium)) l1title("Travel times to PES", size(medium)) ring(2)
*/





****************
**** Median ****
****************

******* ALL *******

/*
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("GDP per capita 2019 (2015 international $)", size(medium)) l1title("Travel times to PES", size(medium)) ring(2)
*/

******* METRO / NON-METRO *******

/*
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Metropolitan"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large" & ISO3 == "`c'", mcolor(red%50)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium" & ISO3 == "`c'", mcolor(navy%50)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) bgcolor(white) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" & ISO3 == "`c'",title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("GDP per capita 2019 (2015 international $)", size(medium)) l1title("Travel times to PES", size(medium)) ring(2)
*/

/*
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if ISO3 == "`c'" & metro_2 =="Non-metropolitan"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro" & ISO3 == "`c'", mcolor(red%50)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote" & ISO3 == "`c'", mcolor(navy%50)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) bgcolor(white) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" & ISO3 == "`c'",title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("GDP per capita 2019 (2015 international $)", size(medium)) l1title("Travel times to PES", size(medium)) ring(2)
*/

*/



//////////////// Income decline travel times PES ///////////////

/
keep if PES_traveltime_driving_bottom20 !=. & GDPpcdecline !=. & country_8 == 1


*******************
**** Bottom 20 ****
*******************

******* ALL *******

/*
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient 
foreach c in `countries' {
	
    corr PES_traveltime_driving_bottom20 GDPpcdecline if ISO3 == "`c'"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) (scatter PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) || lfit PES_traveltime_driving_bottom20 GDPpcdecline if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("Annual GDP growth 2005-2019", size(medium)) l1title("Travel times to PES", size(medium)) ring(2)
*/



****************
**** Median ****
****************

******* ALL *******

/
// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient
foreach c in `countries' {
	
    corr PES_traveltime_driving_median GDPpcdecline if ISO3 == "`c'"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter PES_traveltime_driving_median GDPpcdecline if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) (scatter PES_traveltime_driving_median GDPpcdecline if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) || lfit PES_traveltime_driving_median GDPpcdecline if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("Annual GDP growth 2005-2019", size(medium)) l1title("Travel times to PES", size(medium)) ring(2)
*/


*/

*/

















////////////////// Population decline //////////////////////
/

keep if prim_traveltime_walking_bottom20 !=. & populationdeclinechildren !=. & country_8 == 1


*******************
**** Bottom 20 ****
*******************

******* ALL *******


// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr prim_traveltime_walking_bottom20 populationdeclinechildren if ISO3 == "`c'"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) || lfit prim_traveltime_walking_bottom20 populationdeclinechildren if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("Population children 4 to 9 in 2019 relative to 2005", size(medium)) l1title("Travel times to primary schools - Bottom 20%", size(medium)) ring(2)

graph export mygraph.png, replace

*/

// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr prim_traveltime_walking_bottom20 populationdeclinechildren if ISO3 == "`c'" & metro_2 =="Metropolitan"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_5 == "Metropolitan Large" & ISO3 == "`c'", mcolor(red%50)) (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_5 == "Metropolitan Medium" & ISO3 == "`c'", mcolor(navy%50)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) bgcolor(white) || lfit prim_traveltime_walking_bottom20 populationdeclinechildren if metro_2 =="Metropolitan" & ISO3 == "`c'",title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("Population children 4 to 9 in 2019 relative to 2005", size(medium)) l1title("Travel times to primary schools - Bottom 20%", size(medium)) ring(2)
*/

graph export mygraph.png, replace


// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr prim_traveltime_walking_bottom20 populationdeclinechildren if ISO3 == "`c'" & metro_2 =="Non-metropolitan"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_3 == "Non-metropolitan access to metro" & ISO3 == "`c'", mcolor(red%50)) (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_3 == "Non-metropolitan remote" & ISO3 == "`c'", mcolor(navy%50)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) bgcolor(white) || lfit prim_traveltime_walking_bottom20 populationdeclinechildren if metro_2 =="Non-metropolitan" & ISO3 == "`c'",title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("Population children 4 to 9 in 2019 relative to 2005", size(medium)) l1title("Travel times to primary schools - Bottom 20%", size(medium)) ring(2)
*/

graph export mygraph.png, replace






























keep if care_traveltime_walking_bottom20 !=. & populationdeclinechildren2 !=. & country_8 == 1


*******************
**** Bottom 20 ****
*******************

******* ALL *******


// Create a local macro to store the text labels for each country's regression coefficient
local coefTexts ""
// Get the list of countries
levelsof ISO3, local(countries)
local income_all_
// Iterate over each country, calculate the regression coefficient, 
foreach c in `countries' {
	
    corr care_traveltime_walking_bottom20 populationdeclinechildren2 if ISO3 == "`c'"
    local corr : di %5.3g r(rho)
	
	qui twoway (scatter care_traveltime_walking_bottom20 populationdeclinechildren2 if metro_2 == "Metropolitan" & ISO3 == "`c'", mcolor(black%30)) (scatter care_traveltime_walking_bottom20 populationdeclinechildren2 if metro_2 == "Non-metropolitan" & ISO3 == "`c'", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("") ytitle("") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) bgcolor(white) || lfit care_traveltime_walking_bottom20 populationdeclinechildren2 if ISO3 == "`c'" ,title("`c'", color(black) size (medsmall)) subtitle("correlation: `corr'", size(small)) graphregion(color(white)) name(graph`c', replace)
	
	local income_all_ `income_all_' graph`c'
	di "`income_all_'"
} 

// Combine plots
grc1leg `income_all_',  imargin(1 1 1 1) ycommon xcommon graphregion(color(white)) b2title("Population children 0 to 4 in 2019 relative to 2005", size(medium)) l1title("Travel times to ECEC - Bottom 20%", size(medium)) ring(2)

graph export mygraph.png, replace

*/














































******************************************
















twoway (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019 ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex

twoway (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large", mcolor(red%50)) (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium", mcolor(navy%50)),  ylabel(1(1)10, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) || lfit PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep

twoway (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large", mcolor(red%50)) (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium", mcolor(navy%50)),  ylabel(1(1)10, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) || lfit PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex

twoway (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro", mcolor(black%50)) (scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote", mcolor(brown%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) || lfit PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

twoway (scatter PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro", mcolor(black%50)) (scatter PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote", mcolor(brown%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) || lfit PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex


**** Income travel times ****

keep if prim_traveltime_walking_median !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_10 == 1

twoway (scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to primary schools") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

twoway (scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to primary schools") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex

twoway (scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large", mcolor(red%50)) (scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium", mcolor(navy%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to primary schools") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) || lfit prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep

twoway (scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large", mcolor(red%50)) (scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium", mcolor(navy%50)),  ylabel(1(1)10, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to primary schools") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) || lfit prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex

twoway (scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro", mcolor(black%50)) (scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote", mcolor(brown%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to primary schools") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) || lfit prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

twoway (scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro", mcolor(black%50)) (scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote", mcolor(brown%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to primary schools") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) || lfit prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex


**** Income travel times ****

keep if care_traveltime_walking_median !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_10 == 1

twoway (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to care centres") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to care centres") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex

twoway (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large", mcolor(red%50)) (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium", mcolor(navy%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to care centres") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) || lfit care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep

twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Large", mcolor(red%50)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_5 == "Metropolitan Medium", mcolor(navy%50)),  ylabel(1(1)10, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to care centres") legend(order(1 2) label(1 "Large metropolitan region") label(2 "Medium metropolitan region")) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex

twoway (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro", mcolor(black%50)) (scatter care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote", mcolor(brown%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to care centres") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) || lfit care_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

twoway (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan access to metro", mcolor(black%50)) (scatter care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_3 == "Non-metropolitan remote", mcolor(brown%50)),  ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("GDP per capita 2019 (2015 international $)")  ytitle("Travel times to care centres") legend(order(1 2) label(1 "Non-metropolitan access to metro") label(2 "Non-metropolitan remote")) || lfit care_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan" ||, by(ISO3, note("") graphregion(fcolor(white))) // Annex


**** Income decline travel times ****

keep if PES_traveltime_driving_median !=. & GDPpcdecline !=. & country_10 == 1

twoway (scatter PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 == "Metropolitan", mcolor(black%30)) (scatter PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Annual GDP growth 2005-2019")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit PES_traveltime_driving_bottom20 GDPpcdecline ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

twoway (scatter lnGDP_PC_REAL_PPP_2019 GDPpcdecline if metro_2 == "Metropolitan", mcolor(black%30)) (scatter lnGDP_PC_REAL_PPP_2019 GDPpcdecline if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(9(2)12, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Annual GDP growth 2005-2019")  ytitle("GDP per capita 2019 (2015 international $)") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit lnGDP_PC_REAL_PPP_2019 GDPpcdecline ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

keep if prim_traveltime_walking_bottom20 !=. & GDPpcdecline !=. & country_10 == 1

twoway (scatter prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Annual GDP growth 2005-2019")  ytitle("Travel times to primary schools") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit prim_traveltime_walking_bottom20 GDPpcdecline ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

twoway (scatter prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(9(2)12, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Annual GDP growth 2005-2019")  ytitle("GDP per capita 2019 (2015 international $)") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit lnGDP_PC_REAL_PPP_2019 GDPpcdecline ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 



**** Population decline travel times ****


keep if prim_traveltime_walking_median !=. & populationdecline !=. & country_10 == 1

twoway (scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Population in 2019 relative to 2005")  ytitle("Travel Times") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit prim_traveltime_walking_bottom20 populationdecline ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

keep if prim_traveltime_walking_median !=. & populationdeclinechildren !=. & country_10 == 1

twoway (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_bottom20 populationdeclinechildren if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Population of children 5 to 9 in 2019 relative to 2005")  ytitle("Travel Times") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit prim_traveltime_walking_bottom20 populationdeclinechildren ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 


keep if prim_traveltime_walking_median !=. & populationdecline !=. & country_10 == 1

twoway (scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Population in 2019 relative to 2005")  ytitle("Travel Times") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit prim_traveltime_walking_bottom20 populationdecline ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

keep if care_traveltime_walking_median !=. & populationdeclinechildren !=. & country_10 == 1

twoway (scatter care_traveltime_walking_bottom20 populationdeclinechildren if metro_2 == "Metropolitan", mcolor(black%30)) (scatter care_traveltime_walking_bottom20 populationdeclinechildren if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Population of children 5 to 9 in 2019 relative to 2005")  ytitle("Travel Times") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit care_traveltime_walking_bottom20 populationdeclinechildren ||, by(ISO3, note("") graphregion(fcolor(white)))// Keep 


**** Relative needs *****


keep if PES_traveltime_driving_median !=. & UNEM_RA_15_64_2019 !=. & country_10 == 1

twoway (scatter PES_traveltime_driving_median UNEM_RA_15_64_2019 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter PES_traveltime_driving_median UNEM_RA_15_64_2019 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("popshare5_9")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit PES_traveltime_driving_median UNEM_RA_15_64_2019 ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

keep if prim_traveltime_walking_median !=. & popshare5_9 !=. & country_10 == 1

twoway (scatter prim_traveltime_walking_median popshare5_9 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter prim_traveltime_walking_median popshare5_9 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Population share of children 5 to 9")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit prim_traveltime_walking_median popshare5_9 ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 

keep if care_traveltime_walking_median !=. & popshare0_4 !=. & country_10 == 1

twoway (scatter care_traveltime_walking_median popshare0_4 if metro_2 == "Metropolitan", mcolor(black%30)) (scatter care_traveltime_walking_median popshare0_4 if metro_2 == "Non-metropolitan", mcolor(green%30) symbol(triangle)), ylabel(1(2)13, valuelabel angle (0) labsize(small)) xlabel(,labsize(small)) xtitle("Population share of children 0 to 4")  ytitle("Travel times to PES") legend(order(1 2) label(1 "Metropolitan regions") label(2 "Non-metropolitan regions")) || lfit care_traveltime_walking_median popshare0_4 ||, by(ISO3, note("") graphregion(fcolor(white))) // Keep 


**** Regressions PES *****

egen number_regions = count(tl3_id), by(ISO3)

reg pes_driving_15 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country, robust
reg pes_driving_15 UNEM_RA_15_64_2019 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country, robust

reg pes_driving_15 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [aweight = TOT_POP_2022], robust
reg pes_driving_15 UNEM_RA_15_64_2019 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [aweight = TOT_POP_2022], robust

reg pes_driving_15 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
reg pes_driving_15 UNEM_RA_15_64_2019 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust

reg prim_walking_15 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country, robust
reg prim_walking_15 popshare5_9 populationdeclinechildren lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country, robust

reg prim_walking_15 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [aweight = TOT_POP_2022], robust
reg prim_walking_15 popshare5_9 populationdeclinechildren lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [aweight = TOT_POP_2022], robust

reg prim_walking_15 lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust
reg prim_walking_15 popshare5_9 populationdeclinechildren lnGDP_PC_REAL_PPP_2020 GDPpcdecline lnPOP_DEN_2022 i.metro_5_num i.country [pweight = 1/number_regions], robust


break code


********************************** Previous code ***************************************************











////////////////////////////////////////*****************************************

**** Income travel times ****
/*

keep if PES_traveltime_driving_median !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_8 == 1

twoway scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019|| lfit PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall))  ||, by (country) 
twoway scatter PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019 || lfit PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019, ylabel(1(1)10, valuelabel angle (00) labsize(small))  ||, by (country) 

twoway scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019,  || lfit PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019, ylabel(1(1)13, valuelabel angle (00)) labsize(vsmall)) ||, by (metro_2)
twoway scatter PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019,  || lfit PES_traveltime_driving_median lnGDP_PC_REAL_PPP_2019, ylabel(1(1)10, valuelabel angle (00)) absize(small)) ||, by (metro_2)

keep if PES_traveltime_driving_median !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_16 == 1

twoway scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan",  || lfit PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan", ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
twoway scatter PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan",  || lfit PES_traveltime_driving_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan",  ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)

*/

/*

keep if prim_traveltime_walking_median !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_8 == 1

twoway scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019|| lfit prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall))  ||, by (country) 
twoway scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019 || lfit prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019, ylabel(1(1)10, valuelabel angle (00) labsize(small))  ||, by (country) 

twoway scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019,  || lfit prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (metro_2)
twoway scatter prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019,  || lfit prim_traveltime_walking_median lnGDP_PC_REAL_PPP_2019, ylabel(1(1)10, valuelabel angle (00)) absize(small)) ||, by (metro_2)

keep if prim_traveltime_walking_median !=. & lnGDP_PC_REAL_PPP_2019 !=. & country_16 == 1

twoway scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00) labsize(vsmall))  ||, by (ISO3)
twoway scatter prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_bottom20 lnGDP_PC_REAL_PPP_2019 if metro_2 =="Non-metropolitan",  ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)

*/


**** Income decline travel times ****

/*

keep if PES_traveltime_driving_median !=. & GDPpcdecline !=. & country_8 == 1

twoway scatter PES_traveltime_driving_bottom20 GDPpcdecline|| lfit PES_traveltime_driving_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall))  ||, by (country) 
twoway scatter PES_traveltime_driving_median GDPpcdecline || lfit PES_traveltime_driving_median GDPpcdecline, ylabel(1(1)10, valuelabel angle (00) labsize(small))  ||, by (country) 

twoway scatter PES_traveltime_driving_bottom20 GDPpcdecline,  || lfit PES_traveltime_driving_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (metro_2)
twoway scatter PES_traveltime_driving_median GDPpcdecline,  || lfit PES_traveltime_driving_median GDPpcdecline, ylabel(1(1)10, valuelabel angle (00)) absize(small)) ||, by (metro_2)

keep if PES_traveltime_driving_median !=. & GDPpcdecline !=. & country_16 == 1

twoway scatter PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 == "Metropolitan",  || lfit PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 =="Metropolitan", ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
twoway scatter PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 == "Non-metropolitan",  || lfit PES_traveltime_driving_bottom20 GDPpcdecline if metro_2 =="Non-metropolitan",  ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)

*/

/*

keep if prim_traveltime_walking_median !=. & GDPpcdecline !=. & country_8 == 1

twoway scatter prim_traveltime_walking_bottom20 GDPpcdecline|| lfit prim_traveltime_walking_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall))  ||, by (country) 
twoway scatter PES_traveltime_driving_median GDPpcdecline || lfit prim_traveltime_walking_median GDPpcdecline, ylabel(1(1)10, valuelabel angle (00) labsize(small))  ||, by (country) 

twoway scatter prim_traveltime_walking_bottom20 GDPpcdecline,  || lfit prim_traveltime_walking_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (metro_2)
twoway scatter prim_traveltime_walking_median GDPpcdecline,  || lfit prim_traveltime_walking_median GDPpcdecline, ylabel(1(1)10, valuelabel angle (00)) absize(small)) ||, by (metro_2)

keep if PES_traveltime_driving_median !=. & GDPpcdecline !=. & country_16 == 1

twoway scatter prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 =="Metropolitan", ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
twoway scatter prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_bottom20 GDPpcdecline if metro_2 =="Non-metropolitan",  ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)

*/



**** Population decline ****

/*
keep if PES_traveltime_driving_median !=. & populationdecline !=. & country_8 == 1

twoway scatter PES_traveltime_driving_bottom20 populationdecline|| lfit PES_traveltime_driving_bottom20 populationdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall))  ||, by (country) 
twoway scatter PES_traveltime_driving_median populationdecline || lfit PES_traveltime_driving_median populationdecline, ylabel(1(1)10, valuelabel angle (00) labsize(small))  ||, by (country) 

twoway scatter PES_traveltime_driving_bottom20 populationdecline,  || lfit PES_traveltime_driving_bottom20 populationdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (metro_2)
twoway scatter PES_traveltime_driving_median populationdecline,  || lfit PES_traveltime_driving_median populationdecline, ylabel(1(1)10, valuelabel angle (00) absize(small)) ||, by (metro_2)

keep if PES_traveltime_driving_median !=. & populationdecline !=. & country_16 == 1

twoway scatter PES_traveltime_driving_bottom20 populationdecline if metro_2 == "Metropolitan",  || lfit PES_traveltime_driving_bottom20 populationdecline if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
twoway scatter PES_traveltime_driving_bottom20 populationdecline if metro_2 == "Non-metropolitan",  || lfit PES_traveltime_driving_bottom20 populationdecline if metro_2 =="Non-metropolitan",  ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
*/

/*
keep if prim_traveltime_walking_median !=. & populationdecline !=. & country_8 == 1

twoway scatter prim_traveltime_walking_bottom20 populationdecline|| lfit prim_traveltime_walking_bottom20 populationdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall))  ||, by (country) 
twoway scatter prim_traveltime_walking_median populationdecline || lfit prim_traveltime_walking_median populationdecline, ylabel(1(1)10, valuelabel angle (00) labsize(small))  ||, by (country) 

twoway scatter prim_traveltime_walking_bottom20 populationdecline,  || lfit prim_traveltime_walking_bottom20 populationdecline, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (metro_2)
twoway scatter prim_traveltime_walking_median populationdecline,  || lfit prim_traveltime_walking_median populationdecline, ylabel(1(1)13, valuelabel angle (00) absize(small)) ||, by (metro_2)

keep if PES_traveltime_driving_median !=. & populationdecline !=. & country_16 == 1

twoway scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_bottom20 populationdecline if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
twoway scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_bottom20 populationdecline if metro_2 =="Non-metropolitan",  ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
*/



******* Relative needs ***********

/*
keep if PES_traveltime_driving_median !=. & UNEM_RA_15_64_2019 !=. & country_8 == 1

twoway scatter PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019|| lfit PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall))  ||, by (country) 
twoway scatter PES_traveltime_driving_median UNEM_RA_15_64_2019 || lfit PES_traveltime_driving_median UNEM_RA_15_64_2019, ylabel(1(1)10, valuelabel angle (00) labsize(small))  ||, by (country) 

twoway scatter PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019,  || lfit PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019, ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (metro_2)
twoway scatter PES_traveltime_driving_median UNEM_RA_15_64_2019,  || lfit PES_traveltime_driving_median UNEM_RA_15_64_2019, ylabel(1(1)10, valuelabel angle (00) absize(small)) ||, by (metro_2)

keep if PES_traveltime_driving_median !=. & populationdecline !=. & country_16 == 1

twoway scatter PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019 if metro_2 == "Metropolitan",  || lfit PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019 if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
twoway scatter PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019 if metro_2 == "Non-metropolitan",  || lfit PES_traveltime_driving_bottom20 UNEM_RA_15_64_2019 if metro_2 =="Non-metropolitan",  ylabel(1(1)13, valuelabel angle (00) labsize(vsmall)) ||, by (ISO3)
*/

/*

keep if prim_traveltime_walking_median !=. & popshare5_9 !=. & country_8 == 1

twoway scatter prim_traveltime_walking_median popshare5_9 || lfit prim_traveltime_walking_median popshare5_9, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 
twoway scatter prim_traveltime_walking_bottom20 popshare5_9 || lfit prim_traveltime_walking_bottom20 popshare5_9, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 

twoway scatter prim_traveltime_walking_median popshare5_9 || lfit prim_traveltime_walking_median popshare5_9, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 
twoway scatter prim_traveltime_walking_bottom20 popshare5_9 || lfit prim_traveltime_walking_bottom20 popshare5_9, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 

keep if prim_traveltime_walking_median !=. & populationdecline !=. & country_16 == 1 

twoway scatter prim_traveltime_walking_bottom20 popshare5_9 if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_bottom20 popshare5_9 if metro_2 =="Metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)
twoway scatter prim_traveltime_walking_bottom20 popshare5_9 if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_bottom20 popshare5_9 if metro_2 == "Non-metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)
*/

/*
keep if prim_traveltime_walking_median !=. & KID_WOM_RA_2019 !=. & country_8 == 1

twoway scatter prim_traveltime_walking_median KID_WOM_RA_2019 || lfit prim_traveltime_walking_median KID_WOM_RA_2019, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 
twoway scatter prim_traveltime_walking_bottom20 KID_WOM_RA_2019 || lfit prim_traveltime_walking_bottom20 KID_WOM_RA_2019, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 

twoway scatter prim_traveltime_walking_median populationdecline || lfit prim_traveltime_walking_median populationdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 
twoway scatter prim_traveltime_walking_bottom20 populationdecline || lfit prim_traveltime_walking_bottom20 populationdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 

keep if prim_traveltime_walking_median !=. & populationdecline !=. & country_16 == 1 

twoway scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_bottom20 populationdecline if metro_2 =="Metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)
twoway scatter prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_bottom20 populationdecline if metro_2 == "Non-metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)

*/



*** Mobility ***

/*

drop if INMIG_ALL_RA_2019 > 4 
drop if tl3_id == "FI200"

keep if prim_traveltime_walking_bottom20 !=. & INMIG_ALL_RA_2019 !=. & country_8 == 1

twoway scatter prim_traveltime_walking_median INMIG_ALL_RA_2019 || lfit prim_traveltime_walking_median INMIG_ALL_RA_2019, ylabel(1(1)10, valuelabel angle (00) labsize(small)) ||, by (country) 
twoway scatter prim_traveltime_walking_median INMIG_ALL_RA_2019 || lfit prim_traveltime_walking_median INMIG_ALL_RA_2019, ylabel(1(1)10, valuelabel angle (00) labsize(small)) ||, by (metro_2) 


keep if prim_traveltime_walking_median !=. & populationdecline !=. & country_16 == 1 

twoway scatter prim_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00))  ||, by (ISO3)
twoway scatter prim_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 == "Non-metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)

*/

drop if INMIG_ALL_RA_2019 > 4

keep if care_traveltime_walking_median !=. & INMIG_ALL_RA_2019 !=. & country_8 == 1

twoway scatter care_traveltime_walking_median INMIG_ALL_RA_2019 || lfit care_traveltime_walking_median INMIG_ALL_RA_2019, ylabel(1(1)9, valuelabel angle (00) labsize(small)) ||, by (country) 
twoway scatter care_traveltime_walking_median INMIG_ALL_RA_2019 || lfit care_traveltime_walking_median INMIG_ALL_RA_2019, ylabel(1(1)9, valuelabel angle (00) labsize(small)) ||, by (metro_2) 


keep if care_traveltime_walking_median !=. & populationdecline !=. & country_16 == 1 

twoway scatter care_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 == "Metropolitan",  || lfit care_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00))  ||, by (ISO3)
twoway scatter care_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 == "Non-metropolitan",  || lfit care_traveltime_walking_median INMIG_ALL_RA_2019 if metro_2 == "Non-metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)












////////////////////////////////////// Previous code and other code - mixed //////////////////////









**** Demand ****




histogram prim_traveltime_walking_median if ISO3 == "ESP", by (metro_2)



































**** Total fertility rate ****


keep if prim_traveltime_walking_bottom20 !=. & TF_RA_2019 !=.

twoway scatter prim_traveltime_walking_bottom20 TF_RA_2019 || lfit prim_traveltime_walking_bottom20 TF_RA_2019, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 
twoway scatter prim_traveltime_walking_bottom20 TF_RA_2019 || lfit prim_traveltime_walking_bottom20 TF_RA_2019, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 


keep if prim_traveltime_walking_bottom20 !=. & NETMOB_ALL_RA_2015 !=. & country_16 == 1 & metro_2 == "Non-metropolitan"
twoway scatter prim_traveltime_walking_bottom20 NETMOB_ALL_RA_2015 if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_bottom20 NETMOB_ALL_RA_2015 if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00))  ||, by (ISO3)
twoway scatter prim_traveltime_walking_bottom20 TF_RA_2019 if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_bottom20 TF_RA_2019 if metro_2 == "Non-metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)


keep if care_traveltime_walking_bottom20 !=. & TF_RA_2019 !=.

twoway scatter care_traveltime_walking_bottom20 TF_RA_2019 || lfit prim_traveltime_walking_bottom20 TF_RA_2019, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 
twoway scatter care_traveltime_walking_bottom20 TF_RA_2019 || lfit prim_traveltime_walking_bottom20 TF_RA_2019, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 


keep if care_traveltime_walking_bottom20 !=. & NETMOB_ALL_RA_2015 !=. & country_16 == 1 & metro_2 == "Non-metropolitan"
twoway scatter care_traveltime_walking_bottom20 NETMOB_ALL_RA_2015 if metro_2 == "Metropolitan",  || lfit prim_traveltime_walking_bottom20 NETMOB_ALL_RA_2015 if metro_2 =="Metropolitan", ylabel(1(1)10, valuelabel angle (00))  ||, by (ISO3)
twoway scatter care_traveltime_walking_bottom20 TF_RA_2019 if metro_2 == "Non-metropolitan",  || lfit prim_traveltime_walking_bottom20 TF_RA_2019 if metro_2 == "Non-metropolitan", ylabel(1(1)13, valuelabel angle (00))  ||, by (ISO3)


**** Employment rate gender difference ****



keep if prim_traveltime_walking_bottom20 !=. & EMP_RA_15_64_SEXDIF_2015 !=.

twoway scatter prim_traveltime_walking_bottom20 EMP_RA_15_64_SEXDIF_2015 || lfit prim_traveltime_walking_bottom20 EMP_RA_15_64_SEXDIF_2015, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 
twoway scatter prim_traveltime_walking_bottom20 EMP_RA_15_64_SEXDIF_2015 || lfit prim_traveltime_walking_bottom20 EMP_RA_15_64_SEXDIF_2015, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 


keep if care_traveltime_walking_bottom20 !=. & EMP_RA_15_64_SEXDIF_2015 !=.

twoway scatter care_traveltime_walking_bottom20 EMP_RA_15_64_SEXDIF_2015 || lfit care_traveltime_walking_bottom20 EMP_RA_15_64_SEXDIF_2015, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (country) 








keep if care_traveltime_walking_median !=. & populationdecline !=.


twoway scatter PES_traveltime_driving_median populationdecline || lfit PES_traveltime_driving_median populationdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) ||, by (metro_2) 

keep if PES_traveltime_driving_median !=. & GDPpcdecline !=. & country_16 == 1

twoway scatter PES_traveltime_driving_median GDPpcdecline,  || lfit PES_traveltime_driving_median GDPpcdecline, ylabel(1(1)13, valuelabel angle (00))  ||, by (metro_2 ISO3)

keep if prim_traveltime_walking_median !=. & GDPpcdecline !=.

twoway scatter prim_traveltime_walking_median GDPpcdecline || lfit prim_traveltime_walking_median GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (country) 
twoway scatter prim_traveltime_walking_bottom20 GDPpcdecline || lfit prim_traveltime_walking_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (country) 

twoway scatter prim_traveltime_walking_median GDPpcdecline || lfit prim_traveltime_walking_median GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (metro_2) 
twoway scatter prim_traveltime_walking_bottom20 GDPpcdecline || lfit prim_traveltime_walking_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (metro_2) 

keep if care_traveltime_walking_median !=. & GDPpcdecline !=.

twoway scatter care_traveltime_walking_median GDPpcdecline || lfit care_traveltime_walking_median GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (country) 
twoway scatter care_traveltime_walking_bottom20 GDPpcdecline || lfit care_traveltime_walking_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (country) 

twoway scatter care_traveltime_walking_median GDPpcdecline || lfit care_traveltime_walking_median GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (metro_2) 
twoway scatter care_traveltime_walking_bottom20 GDPpcdecline || lfit care_traveltime_walking_bottom20 GDPpcdecline, ylabel(1(1)13, valuelabel angle (00) labsize(small)) xlabel(-0.05(0.025)0.05) ||, by (metro_2) 

*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 populationdecline || lfit pes_driving_15 populationdecline ||, by (country)  // Keep
twoway scatter PES_driving_bottom20 populationdecline, ylabel(1(1)13, valuelabel angle (0)) || lfit PES_driving_bottom20 populationdecline ||, by (country) // Keep

*keep if bigcountry == 1 & childcare_walking_15 !=.
twoway scatter childcare_walking_15 populationdecline || lfit childcare_walking_15 populationdecline ||, by (country)  // Keep
















twoway scatter pes_driving_15 lnGDP_PC_REAL_PPP_2020 || lfit pes_driving_15 lnGDP_PC_REAL_PPP_2020 // Keep
twoway scatter pes_driving_30 lnGDP_PC_REAL_PPP_2020 || lfit pes_driving_30 lnGDP_PC_REAL_PPP_2020 // Keep

twoway scatter prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 // Keep
twoway scatter prim_edu_walking_30 lnGDP_PC_REAL_PPP_2020 || lfit prim_edu_walking_30 lnGDP_PC_REAL_PPP_2020 // Keep 

twoway scatter childcare_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit childcare_walking_15 lnGDP_PC_REAL_PPP_2020 // Keep
twoway scatter childcare_walking_30 lnGDP_PC_REAL_PPP_2020 || lfit childcare_walking_15 lnGDP_PC_REAL_PPP_2020 // Keep 


*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 lnGDP_PC_REAL_PPP_2020 || lfit pes_driving_15 lnGDP_PC_REAL_PPP_2020 ||, by (country)  // Keep
twoway scatter pes_driving_15 lnGDP_PC_REAL_PPP_2020 || lfit pes_driving_15 lnGDP_PC_REAL_PPP_2020 ||, by (metropolitanin2_string)  // Keep
*keep if verybigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 lnGDP_PC_REAL_PPP_2020 || lfit pes_driving_15 lnGDP_PC_REAL_PPP_2020 ||, by (country metropolitanin2_string)  // Keep



*keep if bigcountry == 1 & prim_edu_walking_15 !=.
twoway scatter prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 ||, by (country)  // Keep
twoway scatter prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 ||, by (metropolitanin2_string)
*keep if verybigcountry == 1 & prim_edu_walking_15 !=.
twoway scatter prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit prim_edu_walking_15 lnGDP_PC_REAL_PPP_2020 ||, by (country metropolitanin2_string)

*keep if bigcountry == 1 & childcare_walking_15 !=.
twoway scatter childcare_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit childcare_walking_15 lnGDP_PC_REAL_PPP_2020 ||, by (country)  // Keep
twoway scatter childcare_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit childcare_walking_15 lnGDP_PC_REAL_PPP_2020 ||, by (metropolitanin3_string)
*keep if verybigcountry == 1 & childcare_walking_15 !=.
twoway scatter childcare_walking_15 lnGDP_PC_REAL_PPP_2020 || lfit childcare_walking_15 lnGDP_PC_REAL_PPP_2020 ||, by (country metropolitanin2_string)



**** Income decline ****

twoway scatter pes_driving_15 GDPpcdecline || lfit pes_driving_15 GDPpcdecline // Keep


twoway scatter PES_driving_median GDPpcdecline, ylabel(1(1)13, valuelabel angle (0)) || lfit PES_driving_bottom20 GDPpcdecline


twoway scatter pes_driving_30 GDPpcdecline || lfit pes_driving_30 GDPpcdecline // Keep

twoway scatter prim_edu_walking_15 GDPpcdecline || lfit prim_edu_walking_15 GDPpcdecline // Keep
twoway scatter prim_edu_walking_30 GDPpcdecline || lfit prim_edu_walking_30 GDPpcdecline // Keep 

twoway scatter childcare_walking_15 GDPpcdecline || lfit childcare_walking_15 GDPpcdecline // Keep
twoway scatter childcare_walking_30 GDPpcdecline || lfit childcare_walking_15 GDPpcdecline // Keep 

*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 GDPpcdecline || lfit pes_driving_15 GDPpcdecline ||, by (country)  // Keep





**** Population and employment decline ****

twoway scatter pes_driving_15 populationdecline || lfit pes_driving_15 populationdecline ||, by (metro_2) // Keep
twoway scatter pes_driving_30 populationdecline || lfit pes_driving_30 populationdecline // Keep

twoway scatter prim_edu_walking_15 populationdecline || lfit prim_edu_walking_15 populationdecline // Keep
twoway scatter prim_edu_walking_30 populationdecline || lfit prim_edu_walking_30 populationdecline // Keep 

twoway scatter childcare_walking_15 populationdecline || lfit childcare_walking_15 populationdecline // Keep
twoway scatter childcare_walking_30 populationdecline || lfit childcare_walking_15 populationdecline // Keep 

*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 populationdecline || lfit pes_driving_15 populationdecline ||, by (country)  // Keep
twoway scatter PES_driving_bottom20 populationdecline, ylabel(1(1)13, valuelabel angle (0)) || lfit PES_driving_bottom20 populationdecline ||, by (country) // Keep

*keep if bigcountry == 1 & childcare_walking_15 !=.
twoway scatter childcare_walking_15 populationdecline || lfit childcare_walking_15 populationdecline ||, by (country)  // Keep








twoway scatter pes_driving_15 employmentdecline || lfit pes_driving_15 employmentdecline // Keep
twoway scatter pes_driving_30 employmentdecline || lfit pes_driving_30 employmentdecline // Keep

twoway scatter prim_edu_walking_15 employmentdecline || lfit prim_edu_walking_15 employmentdecline // Keep
twoway scatter prim_edu_walking_30 employmentdecline || lfit prim_edu_walking_30 employmentdecline // Keep 

twoway scatter childcare_walking_15 employmentdecline || lfit childcare_walking_15 employmentdecline // Keep
twoway scatter childcare_walking_30 employmentdecline || lfit childcare_walking_15 employmentdecline // Keep 

*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 employmentdecline || lfit pes_driving_15 employmentdecline ||, by (country)  // Keep


**** Mobility and immigration ****


twoway scatter pes_driving_15 NETMOB_ALL_RA_2015 || lfit pes_driving_15 NETMOB_ALL_RA_2015 // Keep
twoway scatter pes_driving_30 NETMOB_ALL_RA_2015 || lfit pes_driving_30 NETMOB_ALL_RA_2015 // Keep

*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 NETMOB_ALL_RA_2015 || lfit pes_driving_15 NETMOB_ALL_RA_2015 ||, by (country)  // Keep

twoway scatter prim_edu_walking_15 NETMOB_ALL_RA_2015 || lfit prim_edu_walking_15 NETMOB_ALL_RA_2015 // Keep
twoway scatter prim_edu_walking_30 NETMOB_ALL_RA_2015 || lfit prim_edu_walking_30 NETMOB_ALL_RA_2015 // Keep 

twoway scatter childcare_walking_15 NETMOB_ALL_RA_2015 || lfit childcare_walking_15 NETMOB_ALL_RA_2015 // Keep
twoway scatter childcare_walking_30 NETMOB_ALL_RA_2015 || lfit childcare_walking_15 NETMOB_ALL_RA_2015 // Keep 
*keep if bigcountry == 1 & childcare_walking_15 !=.
twoway scatter childcare_walking_15 NETMOB_ALL_RA_2015 || lfit childcare_walking_15 NETMOB_ALL_RA_2015 ||, by (country)  // Keep



**** Total fertility rate ****

twoway scatter prim_edu_walking_15 YOU_DEP_RA2020 || lfit prim_edu_walking_15 YOU_DEP_RA2020 // Keep
twoway scatter prim_edu_walking_30 YOU_DEP_RA2020 || lfit prim_edu_walking_30 YOU_DEP_RA2020 // Keep 

twoway scatter childcare_walking_15 YOU_DEP_RA2020 || lfit childcare_walking_15 YOU_DEP_RA2020 // Keep
twoway scatter childcare_walking_30 YOU_DEP_RA2020 || lfit childcare_walking_15 YOU_DEP_RA2020 // Keep 

twoway scatter prim_edu_walking_15 KID_WOM_RA_2020 || lfit prim_edu_walking_15 KID_WOM_RA_2020 // Keep
twoway scatter prim_edu_walking_30 KID_WOM_RA_2020 || lfit prim_edu_walking_30 KID_WOM_RA_2020 // Keep 

twoway scatter childcare_walking_15 KID_WOM_RA_2020 || lfit childcare_walking_15 KID_WOM_RA_2020 // Keep
twoway scatter childcare_walking_30 KID_WOM_RA_2020 || lfit childcare_walking_15 KID_WOM_RA_2020 // Keep 




*keep if bigcountry == 1 & prim_edu_walking_15 !=.
twoway scatter prim_edu_walking_15 YOU_DEP_RA2020 || lfit prim_edu_walking_15 YOU_DEP_RA2020 ||, by (country)  // Keep
twoway scatter prim_edu_walking_15 KID_WOM_RA_2020 || lfit prim_edu_walking_15 KID_WOM_RA_2020 ||, by (country)  // Keep


*keep if bigcountry == 1 & childcare_walking_15 !=.
twoway scatter childcare_walking_15 YOU_DEP_RA2020 || lfit childcare_walking_15 YOU_DEP_RA2020 ||, by (country)  // Keep
twoway scatter childcare_walking_15 KID_WOM_RA_2020 || lfit childcare_walking_15 KID_WOM_RA_2020 ||, by (country)  // Keep






























twoway scatter pes_driving_15 EMP_RA_15_64_SEXDIF_2015 || lfit pes_driving_15 EMP_RA_15_64_SEXDIF_2015 // Keep
twoway scatter pes_driving_30 EMP_RA_15_64_SEXDIF_2015 || lfit pes_driving_30 EMP_RA_15_64_SEXDIF_2015 // Keep
*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 EMP_RA_15_64_SEXDIF_2015 || lfit pes_driving_15 EMP_RA_15_64_SEXDIF_2015 ||, by (country)  // Keep



twoway scatter prim_walking_15 EMP_RA_15_64_SEXDIF_2015 || lfit prim_walking_15 EMP_RA_15_64_SEXDIF_2015 // Keep




















twoway scatter prim_walking_30 EMP_RA_15_64_SEXDIF_2015 || lfit prim_walking_30 EMP_RA_15_64_SEXDIF_2015 // Keep 
keep if bigcountry == 1 & prim_edu_walking_15 !=. & EMP_RA_15_64_SEXDIF_2015 !=.
twoway scatter prim_edu_walking_15 EMP_RA_15_64_SEXDIF_2015 || lfit prim_edu_walking_15 EMP_RA_15_64_SEXDIF_2015 ||, by (country)  // Keep


twoway scatter childcare_walking_15 EMP_RA_15_64_SEXDIF_2015 || lfit childcare_walking_15 EMP_RA_15_64_SEXDIF_2015 // Keep
twoway scatter childcare_walking_30 EMP_RA_15_64_SEXDIF_2015 || lfit childcare_walking_15 EMP_RA_15_64_SEXDIF_2015 // Keep 
keep if bigcountry == 1 & childcare_walking_15 !=. & EMP_RA_15_64_SEXDIF_2015 !=.
twoway scatter childcare_walking_15 UNEM_RA_15_64_SEXDIF_2015 || lfit childcare_walking_15 EMP_RA_15_64_SEXDIF_2015 ||, by (country)  // Keep





*** Unemployment rate and PES 




keep if bigcountry == 1 & pes_driving_15 !=. & UNEM_RA_15_64_2015 !=.
twoway scatter pes_driving_15 UNEM_RA_15_64_2015 || lfit pes_driving_15 UNEM_RA_15_64_2015 ||, by (country)  // Keep
twoway scatter PES_driving_bottom20 UNEM_RA_15_64_2015, ylabel(1(1)13, valuelabel angle (0)) || lfit PES_driving_bottom20 UNEM_RA_15_64_2015 ||, by (country) // Keep



keep if bigcountry == 1 & pes_driving_15 !=. & UNEM_RA_15_64_2021 !=.
twoway scatter pes_driving_15 UNEM_RA_15_64_2021 || lfit pes_driving_15 UNEM_RA_15_64_2021 ||, by (country)  // Keep
twoway scatter PES_driving_bottom20 UNEM_RA_15_64_2021, ylabel(1(1)13, valuelabel angle (0)) || lfit PES_driving_bottom20 UNEM_RA_15_64_2021 ||, by (country) // Keep



**** Metro / Non-metro *****

histogram PES_traveltime_driving_bottom20, by (metro_4, col(1)) xlabel(1(1)13, valuelabel angle(90)) ylabel(0(0.2)0.5) discrete // Keep  
histogram PES_traveltime_driving_median, by (metro_4, col(1)) xlabel(1(1)11, valuelabel angle(90)) ylabel(0(0.2)0.5) discrete // Keep  

histogram prim_walking_bottom20, by (metro_3, col(1)) xlabel(1(1)13, valuelabel angle(90)) ylabel(0(0.2)0.5) discrete // Keep  
histogram prim_walking_median, by (metro_3, col(1)) xlabel(1(1)11, valuelabel angle(90)) ylabel(0(0.2)0.5) discrete // Keep 

histogram care_walking_bottom20, by (metro_3, col(1)) xlabel(1(1)12, valuelabel angle(90)) ylabel(0(0.2)0.5) discrete // Keep  
histogram care_walking_median, by (metro_3, col(1)) xlabel(1(1)11, valuelabel angle(90)) ylabel(0(0.2)0.5) discrete // Keep 

**** Population density *****

twoway scatter PES_traveltime_driving_bottom20 lnPOP_DEN_2022, ylabel(1(1)13, valuelabel angle (0)) || lfit PES_traveltime_driving_bottom20 lnPOP_DEN_2022
twoway scatter PES_traveltime_driving_median lnPOP_DEN_2022, ylabel(1(1)11, valuelabel angle (0)) || lfit PES_traveltime_driving_median lnPOP_DEN_2022



 // Do not keep, example of why not to use scatterplots
twoway scatter lnPOP_DEN_2022 PES_driving_bottom20, xlabel(1(1)13, valuelabel angle (90))  // Do not keep, example of why not to use scatterplots

twoway scatter pes_driving_15 lnPOP_DEN_2022 || lfit pes_driving_15 lnPOP_DEN_2022 // Keep
twoway scatter pes_driving_30 lnPOP_DEN_2022 || lfit pes_driving_30 lnPOP_DEN_2022 // Keep

twoway scatter prim_edu_walking_15 lnPOP_DEN_2022 || lfit prim_edu_walking_15 lnPOP_DEN_2022 // Keep
twoway scatter prim_edu_walking_30 lnPOP_DEN_2022 || lfit prim_edu_walking_30 lnPOP_DEN_2022 // Keep 

twoway scatter childcare_walking_15 lnPOP_DEN_2022 || lfit childcare_walking_15 lnPOP_DEN_2022 // Keep
twoway scatter childcare_walking_30 lnPOP_DEN_2022 || lfit childcare_walking_30 lnPOP_DEN_2022 // Keep 



*keep if bigcountry == 1 & pes_driving_15 !=.
twoway scatter pes_driving_15 lnPOP_DEN_2022 || lfit pes_driving_15 lnPOP_DEN_2022 ||, by (country)  // Keep

*keep if bigcountry == 1 & prim_edu_walking_15 !=.
twoway scatter prim_edu_walking_15 lnPOP_DEN_2022 || lfit prim_edu_walking_15 lnPOP_DEN_2022 ||, by (country)  // Keep

*keep if bigcountry == 1 & childcare_walking_15 !=.
twoway scatter childcare_walking_15 lnPOP_DEN_2022 || lfit childcare_walking_15 lnPOP_DEN_2022 ||, by (country)  // Keep



