# US City Open Crime Data Sources

## Tier 1: Full Crime API/CSV (Incident-Level Data)

| # | City | Pop. | Portal URL | Crime Data |
|---|------|------|------------|------------|
| 1 | **New York** | 8.3M | https://opendata.cityofnewyork.us/ | ✅ NYPD Complaint Data (7M+ records) |
| 2 | **Los Angeles** | 3.9M | https://data.lacity.org/ | ✅ LAPD Crime Data 2020-Present |
| 3 | **Chicago** | 2.7M | https://data.cityofchicago.org/ | ✅ Crimes 2001-Present (8M+ records) |
| 4 | **Houston** | 2.3M | https://data.houstontx.gov/ | ✅ HPD Crime Statistics |
| 5 | **Phoenix** | 1.6M | https://www.phoenixopendata.com/ | ✅ Crime Data by Neighborhood |
| 6 | **Philadelphia** | 1.6M | https://www.opendataphilly.org/ | ✅ Crime Incidents |
| 7 | **San Antonio** | 1.5M | https://data.sanantonio.gov/ | ✅ SAPD Calls & Reports |
| 8 | **San Diego** | 1.4M | https://data.sandiego.gov/ | ✅ PD Calls for Service |
| 9 | **Dallas** | 1.3M | https://www.dallasopendata.com/ | ✅ Police Incidents |
| 10 | **San Jose** | 1.0M | https://data.sanjoseca.gov/ | ✅ Police Calls |
| 11 | **Austin** | 1.0M | https://data.austintexas.gov/ | ✅ APD Crime Reports |
| 12 | **San Francisco** | 870K | https://datasf.org/ | ✅ SFPD Incident Reports |
| 13 | **Seattle** | 750K | https://data.seattle.gov/ | ✅ SPD Crime Data |
| 14 | **Denver** | 715K | https://opendata-geospatialdenver.hub.arcgis.com/ | ✅ DPD Crime Data |
| 15 | **Boston** | 675K | https://data.boston.gov/ | ✅ Crime Incident Reports |
| 16 | **Nashville** | 690K | https://data.nashville.gov/ | ✅ Metro PD Incidents |
| 17 | **Baltimore** | 570K | https://data.baltimorecity.gov/ | ✅ BPD Part 1 Crime |
| 18 | **Louisville** | 620K | https://data.louisvilleky.gov/ | ✅ LMPD Crime Data |
| 19 | **Portland** | 650K | https://www.portland.gov/open-data | ✅ PPB Crime Stats |
| 20 | **Las Vegas** | 640K | https://opendata-lasvegas.opendata.arcgis.com/ | ✅ LVMPD Crime |
| 21 | **Detroit** | 640K | https://data.detroitmi.gov/ | ✅ DPD Crime Incidents |
| 22 | **Memphis** | 630K | https://data.memphistn.gov/ | ✅ MPD Crime Data |
| 23 | **Oklahoma City** | 680K | https://data.okc.gov/ | ✅ OKCPD Reports |
| 24 | **Atlanta** | 500K | http://gis.atlantaga.gov/ | ✅ APD Crime Data |
| 25 | **Kansas City** | 500K | https://data.kcmo.org/ | ✅ KCPD Crime Data |
| 26 | **Sacramento** | 525K | https://data.cityofsacramento.org/ | ✅ SPD Calls |
| 27 | **Miami** | 440K | https://gis-mdc.opendata.arcgis.com/ | ✅ Crime Reports |
| 28 | **New Orleans** | 385K | https://datadriven.nola.gov/ | ✅ NOPD Calls & Crime |
| 29 | **Minneapolis** | 425K | https://opendata.minneapolismn.gov/ | ✅ MPD Crime Data |
| 30 | **Cleveland** | 370K | https://data.clevelandohio.gov/ | ✅ CPD Crime |
| 31 | **Raleigh** | 475K | https://data.raleighnc.gov/ | ✅ RPD Incidents |
| 32 | **Oakland** | 430K | https://data.oaklandca.gov/ | ✅ OPD Crime Reports |
| 33 | **Tucson** | 545K | https://data.tucsonaz.gov/ | ✅ TPD Crime Stats |
| 34 | **Omaha** | 485K | https://dataomaha.com/ | ✅ OPD Crime Data |
| 35 | **Long Beach** | 465K | https://data.longbeach.gov/ | ✅ LBPD Crime |
| 36 | **Virginia Beach** | 460K | https://data.vbgov.com/ | ✅ VBPD Calls |
| 37 | **Charlotte** | 875K | https://data.charlottenc.gov/ | ✅ CMPD Incidents |
| 38 | **Indianapolis** | 880K | https://data.indy.gov/ | ✅ IMPD Crime |
| 39 | **Columbus** | 905K | https://opendata.columbus.gov/ | ✅ CPD Crime |
| 40 | **Fort Worth** | 935K | https://data.fortworthtexas.gov/ | ✅ FWPD Reports |
| 41 | **Jacksonville** | 950K | https://data.coj.net/ | ✅ JSO Crime |

## Tier 2: County-Level or Partial Data

| # | City | Pop. | Portal URL | Notes |
|---|------|------|------------|-------|
| 42 | **Fresno** | 540K | County data only | Via Fresno County |
| 43 | **Mesa** | 505K | https://data.mesaaz.gov/ | Limited crime |
| 44 | **Arlington TX** | 395K | Via Tarrant County | County-level |
| 45 | **Albuquerque** | 565K | https://www.cabq.gov/abq-data/ | APD data available |
| 46 | **Colorado Springs** | 485K | https://coloradosprings.gov/opendata | CSPD reports |
| 47 | **Bakersfield** | 400K | Kern County data | County-level |
| 48 | **Tampa** | 395K | https://data.tampagov.net/ | TPD crime |
| 49 | **Aurora CO** | 385K | Via Denver/Adams | Partial |
| 50 | **Wichita** | 395K | https://www.wichita.gov/opendata | WPD data |

## Direct API Endpoints (Best Quality)

### Chicago (Gold Standard)
```
https://data.cityofchicago.org/resource/ijzp-q8t2.json
# Crimes 2001-Present, 8M+ records
# Fields: date, block, iucr, primary_type, description, location_description, arrest, domestic, beat, district, ward, community_area, year, latitude, longitude
```

### NYC
```
https://data.cityofnewyork.us/resource/qgea-i56i.json
# NYPD Complaint Data Current YTD
# Fields: cmplnt_num, boro_nm, addr_pct_cd, loc_of_occur_desc, pd_cd, pd_desc, ky_cd, ofns_desc, law_cat_cd, latitude, longitude
```

### Los Angeles
```
https://data.lacity.org/resource/2nrs-mtv8.json
# Crime Data 2020-Present
# Fields: dr_no, date_rptd, date_occ, time_occ, area, area_name, crm_cd, crm_cd_desc, vict_age, vict_sex, premis_cd, weapon_used_cd, location, lat, lon
```

### San Francisco
```
https://data.sfgov.org/resource/wg3w-h783.json
# Police Department Incident Reports 2018-Present
# Fields: incident_datetime, incident_category, incident_subcategory, incident_description, resolution, police_district, latitude, longitude
```

### Seattle
```
https://data.seattle.gov/resource/tazs-3rd5.json
# SPD Crime Data 2008-Present
# Fields: report_number, offense_start_datetime, crime_against_category, offense_parent_group, offense, offense_code, precinct, sector, beat, mcpp, longitude, latitude
```

### Boston
```
https://data.boston.gov/api/3/action/datastore_search?resource_id=12cb3883-56f5-47de-afa5-3b1cf61b257b
# Crime Incident Reports 2015-Present
# Fields: INCIDENT_NUMBER, OFFENSE_CODE, OFFENSE_CODE_GROUP, OFFENSE_DESCRIPTION, DISTRICT, REPORTING_AREA, SHOOTING, OCCURRED_ON_DATE, YEAR, MONTH, DAY_OF_WEEK, HOUR, Lat, Long
```

### Denver
```
https://www.denvergov.org/media/gis/DataCatalog/crime/csv/crime.csv
# Direct CSV download
# Fields: INCIDENT_ID, OFFENSE_ID, OFFENSE_CODE, OFFENSE_CODE_EXTENSION, OFFENSE_TYPE_ID, OFFENSE_CATEGORY_ID, FIRST_OCCURRENCE_DATE, LAST_OCCURRENCE_DATE, REPORTED_DATE, INCIDENT_ADDRESS, GEO_X, GEO_Y, GEO_LON, GEO_LAT, DISTRICT_ID, PRECINCT_ID, NEIGHBORHOOD_ID, IS_CRIME, IS_TRAFFIC
```

### Philadelphia
```
https://phl.carto.com/api/v2/sql?q=SELECT * FROM incidents_part1_part2 WHERE dispatch_date >= '2020-01-01' LIMIT 10000
# Carto SQL API
```

## FBI UCR Data (Aggregated - Free)

**For cities WITHOUT open portals:**
```
https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/downloads
# Annual data by agency
# Covers ALL US jurisdictions
# Less granular (no addresses), but comprehensive
```

## Data Quality Notes

### Best APIs (incident-level, coordinates, recent):
1. Chicago - 8M+ records, excellent API
2. Los Angeles - Clean, well-documented
3. NYC - Massive dataset, NYPD detail
4. San Francisco - Good categorization
5. Seattle - Long history, good fields

### Challenges:
- Some cities use Socrata (data.cityof*.gov) = easy API
- Some use ArcGIS Hub = need to find FeatureServer endpoints
- Some only have PDFs or annual reports = manual extraction needed

## Recommended Aggregation Strategy

1. **Start with Socrata cities** (easiest API): Chicago, NYC, LA, SF, Seattle, Austin, Denver, Boston, Baltimore, Nashville, Louisville
2. **Add ArcGIS cities**: Phoenix, Las Vegas, Charlotte, Miami
3. **Supplement with FBI UCR** for remaining cities
4. **Scrape/manual** for cities with only PDF reports

## Estimated Coverage

With the 50 cities above:
- **Population covered**: ~85M people (25% of US)
- **Major metros**: 90% of top 50 covered
- **Data freshness**: Most update monthly or weekly
