# Business Analysis — Query Results

> Northstar Wealth Analytics · All data is **100 % synthetic** (SEED=42)
> Queries: `sql/analysis/q01..q14`

---

## Q1 — Headline KPIs

**Business question:** How big is the book today?

| as_of      | total_aum_cr | active_clients | avg_aum_per_client_lakh |
|------------|-------------:|---------------:|------------------------:|
| 2025-12-31 |      7 360.9 |          4 419 |                   166.6 |

---

## Q2 — AUM by Segment and Asset Class (Latest Month)

**Business question:** Where does the money sit, and how is each segment allocated?

| segment       | asset_class | aum_cr  | pct_of_segment | pct_of_firm |
|---------------|-------------|--------:|---------------:|------------:|
| HNI           | Equity      | 1 128.9 |           46.3 |        15.3 |
| HNI           | Debt        |   820.3 |           33.7 |        11.1 |
| HNI           | Liquid      |   248.2 |           10.2 |         3.4 |
| HNI           | Gold        |   240.3 |            9.9 |         3.3 |
| Mass Affluent | Equity      |   417.2 |           45.3 |         5.7 |
| Mass Affluent | Debt        |   320.6 |           34.8 |         4.4 |
| Mass Affluent | Liquid      |    93.7 |           10.2 |         1.3 |
| Mass Affluent | Gold        |    90.2 |            9.8 |         1.2 |
| UHNI          | Equity      | 1 827.3 |           45.7 |        24.8 |
| UHNI          | Debt        | 1 363.0 |           34.1 |        18.5 |
| UHNI          | Liquid      |   409.7 |           10.2 |         5.6 |
| UHNI          | Gold        |   401.4 |           10.0 |         5.5 |

---

## Q3 — Monthly AUM Trend with Growth Rates

**Business question:** How fast is the book growing?

| snapshot_date | aum_cr  | mom_growth_pct | yoy_growth_pct |
|---------------|--------:|---------------:|---------------:|
| 2023-12-31    | 5 161.0 |            — |             — |
| 2024-01-31    | 5 302.2 |          2.74 |             — |
| 2024-02-29    | 5 362.4 |          1.13 |             — |
| 2024-03-31    | 5 471.6 |          2.04 |             — |
| 2024-04-30    | 5 510.9 |          0.72 |             — |
| 2024-05-31    | 5 618.0 |          1.94 |             — |
| 2024-06-30    | 5 690.1 |          1.28 |             — |
| 2024-07-31    | 5 763.6 |          1.29 |             — |
| 2024-08-31    | 5 846.1 |          1.43 |             — |
| 2024-09-30    | 6 040.3 |          3.32 |             — |
| 2024-10-31    | 6 174.8 |          2.23 |             — |
| 2024-11-30    | 6 270.5 |          1.55 |             — |
| 2024-12-31    | 6 364.7 |          1.50 |         23.3 |
| 2025-01-31    | 6 511.9 |          2.31 |         22.8 |
| 2025-02-28    | 6 621.5 |          1.68 |         23.5 |
| 2025-03-31    | 6 498.1 |         -1.86 |         18.8 |
| 2025-04-30    | 6 414.4 |         -1.29 |         16.4 |
| 2025-05-31    | 6 572.9 |          2.47 |         17.0 |
| 2025-06-30    | 6 777.0 |          3.11 |         19.1 |
| 2025-07-31    | 6 929.6 |          2.25 |         20.2 |
| 2025-08-31    | 7 076.0 |          2.11 |         21.0 |
| 2025-09-30    | 7 097.4 |          0.30 |         17.5 |
| 2025-10-31    | 7 182.8 |          1.20 |         16.3 |
| 2025-11-30    | 7 274.2 |          1.27 |         16.0 |
| 2025-12-31    | 7 360.9 |          1.19 |         15.7 |

---

## Q4 — AUM Bridge (Opening → NNA → Market Movement → Closing)

**Business question:** Is growth coming from advisors winning new money (net new assets) or from markets going up?

| month_end  | opening_cr | net_new_assets_cr | market_movement_cr | closing_cr |
|------------|----------:|-----------------:|------------------:|----------:|
| 2024-01-31 |    5 161.0 |             44.5 |              96.8 |    5 302.2 |
| 2024-02-29 |    5 302.2 |             57.9 |               2.2 |    5 362.4 |
| 2024-03-31 |    5 362.4 |             19.5 |              89.8 |    5 471.6 |
| 2024-04-30 |    5 471.6 |             25.1 |              14.2 |    5 510.9 |
| 2024-05-31 |    5 510.9 |             43.9 |              63.3 |    5 618.0 |
| 2024-06-30 |    5 618.0 |             41.8 |              30.3 |    5 690.1 |
| 2024-07-31 |    5 690.1 |             57.7 |              15.9 |    5 763.6 |
| 2024-08-31 |    5 763.6 |             42.5 |              39.9 |    5 846.1 |
| 2024-09-30 |    5 846.1 |            126.4 |              67.8 |    6 040.3 |
| 2024-10-31 |    6 040.3 |             35.0 |              99.5 |    6 174.8 |
| 2024-11-30 |    6 174.8 |             63.8 |              31.9 |    6 270.5 |
| 2024-12-31 |    6 270.5 |             43.8 |              50.4 |    6 364.7 |
| 2025-01-31 |    6 364.7 |             63.0 |              84.2 |    6 511.9 |
| 2025-02-28 |    6 511.9 |              6.8 |             102.8 |    6 621.5 |
| 2025-03-31 |    6 621.5 |             58.6 |            -182.0 |    6 498.1 |
| 2025-04-30 |    6 498.1 |             42.2 |            -125.9 |    6 414.4 |
| 2025-05-31 |    6 414.4 |             40.2 |             118.3 |    6 572.9 |
| 2025-06-30 |    6 572.9 |             83.6 |             120.5 |    6 777.0 |
| 2025-07-31 |    6 777.0 |             47.5 |             105.1 |    6 929.6 |
| 2025-08-31 |    6 929.6 |             64.1 |              82.3 |    7 076.0 |
| 2025-09-30 |    7 076.0 |             60.9 |             -39.4 |    7 097.4 |
| 2025-10-31 |    7 097.4 |             50.9 |              34.4 |    7 182.8 |
| 2025-11-30 |    7 182.8 |            -34.3 |             125.7 |    7 274.2 |
| 2025-12-31 |    7 274.2 |             49.2 |              37.5 |    7 360.9 |

---

## Q5 — Net New Assets by Quarter and Transaction Type

**Business question:** How much is coming in via SIPs vs lump sums, and how much is leaving through redemptions?

| quarter_start | sip_cr | lumpsum_cr | redemptions_cr | net_new_assets_cr |
|---------------|------:|-----------:|---------------:|------------------:|
| 2024-01-01    |  84.6 |      183.3 |          146.1 |             121.9 |
| 2024-04-01    |  85.5 |      177.6 |          152.3 |             110.8 |
| 2024-07-01    |  86.4 |      270.4 |          130.2 |             226.6 |
| 2024-10-01    |  89.5 |      198.7 |          145.6 |             142.6 |
| 2025-01-01    |  91.1 |      217.2 |          179.9 |             128.4 |
| 2025-04-01    |  85.0 |      268.8 |          187.8 |             166.0 |
| 2025-07-01    |  83.5 |      271.6 |          182.7 |             172.5 |
| 2025-10-01    |  84.1 |      195.3 |          213.6 |              65.8 |

---

## Q6 — Top 10 Advisors by AUM

**Business question:** Who manages the most client money?

| aum_rank | advisor_id | advisor_name     | branch    | active_clients | aum_cr | avg_aum_per_client_lakh |
|---------:|------------|------------------|-----------|---------------:|-------:|------------------------:|
|        1 | ADV005     | Viraj Tiwari     | Mumbai    |            233 |  518.6 |                   222.6 |
|        2 | ADV001     | Aryan Maharaj    | Mumbai    |            238 |  405.6 |                   170.4 |
|        3 | ADV002     | Udant Dewan      | Mumbai    |            211 |  384.0 |                   182.0 |
|        4 | ADV004     | Ayushman Chander | Mumbai    |            228 |  341.2 |                   149.6 |
|        5 | ADV003     | Gagan Sami       | Mumbai    |            185 |  272.7 |                   147.4 |
|        6 | ADV010     | Gayathri Chaudry | Delhi NCR |            149 |  260.7 |                   175.0 |
|        7 | ADV016     | Chakradev Kari   | Pune      |            104 |  244.0 |                   234.7 |
|        8 | ADV013     | Tripti Yadav     | Bengaluru |            129 |  240.2 |                   186.2 |
|        9 | ADV015     | Janaki Handa     | Bengaluru |            126 |  228.9 |                   181.7 |
|       10 | ADV023     | Anamika Kanda    | Hyderabad |             96 |  220.9 |                   230.1 |

---

## Q7 — Advisors with the Highest Client Churn

**Business question:** Are some advisors losing clients faster than the firm average?

| advisor_id | advisor_name     | branch    | total_clients | churned_clients | churn_rate_pct | pts_vs_firm_average |
|------------|------------------|-----------|-------------:|----------------:|---------------:|--------------------:|
| ADV007     | Saumya Mall      | Delhi NCR |          142 |              37 |           26.1 |               14.4 |
| ADV023     | Anamika Kanda    | Hyderabad |          126 |              30 |           23.8 |               12.2 |
| ADV031     | Theodore Devi    | Kolkata   |          111 |              21 |           18.9 |                7.3 |
| ADV003     | Gagan Sami       | Mumbai    |          220 |              35 |           15.9 |                4.3 |
| ADV005     | Viraj Tiwari     | Mumbai    |          275 |              42 |           15.3 |                3.7 |
| ADV010     | Gayathri Chaudry | Delhi NCR |          174 |              25 |           14.4 |                2.7 |
| ADV025     | Diya Rattan      | Hyderabad |          106 |              15 |           14.2 |                2.5 |
| ADV004     | Ayushman Chander | Mumbai    |          265 |              37 |           14.0 |                2.3 |
| ADV040     | Yashica Cherian  | Ahmedabad |           80 |              11 |           13.8 |                2.1 |
| ADV018     | Lajita Mall      | Pune      |          103 |              14 |           13.6 |                2.0 |

---

## Q8 — Churn by Dimension (Segment / Risk Profile / Acquisition Channel)

**Business question:** Who churns — and through which channel did they arrive?

| dimension           | value            | clients | churned | churn_rate_pct |
|---------------------|------------------|--------:|--------:|---------------:|
| acquisition_channel | Digital          |   1 314 |     239 |           18.2 |
| acquisition_channel | Corporate Tie-up |     725 |      76 |           10.5 |
| acquisition_channel | Branch Walk-in   |   1 215 |     126 |           10.4 |
| acquisition_channel | Referral         |   1 746 |     140 |            8.0 |
| risk_profile        | Aggressive       |   1 203 |     164 |           13.6 |
| risk_profile        | Conservative     |   1 503 |     167 |           11.1 |
| risk_profile        | Moderate         |   2 294 |     250 |           10.9 |
| segment             | Mass Affluent    |   3 532 |     460 |           13.0 |
| segment             | HNI              |   1 182 |     108 |            9.1 |
| segment             | UHNI             |     286 |      13 |            4.5 |

---

## Q9 — Churn Timeline and AUM Lost

**Business question:** When did clients leave, and how much money left with them?

| churn_month | churned_clients | aum_lost_cr | avg_aum_lost_lakh |
|-------------|----------------:|------------:|------------------:|
| 2024-01-01  |              19 |        15.9 |              83.6 |
| 2024-02-01  |              18 |         9.8 |              54.6 |
| 2024-03-01  |              25 |        35.6 |             142.6 |
| 2024-04-01  |              30 |        29.3 |              97.7 |
| 2024-05-01  |              17 |         9.3 |              54.7 |
| 2024-06-01  |              22 |         9.0 |              40.8 |
| 2024-07-01  |              20 |        10.9 |              54.7 |
| 2024-08-01  |              23 |        14.0 |              60.7 |
| 2024-09-01  |              25 |        19.3 |              77.1 |
| 2024-10-01  |              28 |        14.5 |              51.9 |
| 2024-11-01  |              26 |        11.9 |              45.7 |
| 2024-12-01  |              10 |        10.5 |             105.2 |
| 2025-01-01  |              24 |         7.1 |              29.7 |
| 2025-02-01  |              25 |        42.3 |             169.0 |
| 2025-03-01  |              27 |        39.0 |             144.5 |
| 2025-04-01  |              34 |        30.6 |              90.0 |
| 2025-05-01  |              29 |        46.7 |             160.9 |
| 2025-06-01  |              27 |         8.8 |              32.4 |
| 2025-07-01  |              34 |        54.0 |             158.9 |
| 2025-08-01  |              21 |        20.5 |              97.8 |
| 2025-09-01  |              25 |        22.6 |              90.3 |
| 2025-10-01  |              22 |        14.2 |              64.4 |
| 2025-11-01  |              26 |        83.5 |             321.2 |
| 2025-12-01  |              24 |        15.1 |              63.1 |

---

## Q10 — Dormant Clients

**Business question:** How much AUM belongs to active clients with no transaction in the last 180 days?

| segment       | dormant_clients | dormant_aum_cr | pct_of_firm_aum |
|---------------|----------------:|---------------:|----------------:|
| UHNI          |              53 |          804.3 |            10.9 |
| HNI           |             201 |          404.3 |             5.5 |
| Mass Affluent |             522 |          149.0 |             2.0 |

**Totals:** 776 dormant clients, Rs 1,357.6 Cr dormant AUM (18.4 % of firm AUM)

---

## Q11 — AUM Concentration by Decile

**Business question:** How dependent is the firm on its biggest clients?

| decile | clients | aum_cr  | pct_of_aum | cumulative_pct |
|-------:|--------:|--------:|-----------:|---------------:|
|      1 |     442 | 4 748.6 |       64.5 |           64.5 |
|      2 |     442 | 1 103.3 |       15.0 |           79.5 |
|      3 |     442 |   587.3 |        8.0 |           87.5 |
|      4 |     442 |   260.4 |        3.5 |           91.0 |
|      5 |     442 |   177.3 |        2.4 |           93.4 |
|      6 |     442 |   143.0 |        1.9 |           95.4 |
|      7 |     442 |   119.0 |        1.6 |           97.0 |
|      8 |     442 |    96.2 |        1.3 |           98.3 |
|      9 |     442 |    76.2 |        1.0 |           99.3 |
|     10 |     441 |    49.7 |        0.7 |          100.0 |

---

## Q12 — Suitability Flags (Conservative Clients with >40 % Equity)

**Business question:** Which clients' portfolios no longer match their stated risk profile?

| client_id | full_name              | segment | advisor_name      | equity_pct | aum_lakh |
|-----------|------------------------|---------|-------------------|-----------:|---------:|
| C02921    | Logan Panchal          | UHNI    | Hemangini Lalla   |       44.9 |  1 677.9 |
| C00593    | Vasana Viswanathan     | UHNI    | Janaki Handa      |       50.2 |  1 674.2 |
| C01365    | Harita Ray             | UHNI    | Janaki Handa      |       50.0 |  1 657.8 |
| C01434    | Garima Chad            | UHNI    | Lajita Chatterjee |       56.4 |  1 651.1 |
| C00158    | Wyatt Shroff           | UHNI    | Aryan Maharaj     |       45.3 |  1 340.4 |
| C02929    | Chanakya Arya          | UHNI    | Aryan Maharaj     |       43.6 |  1 327.8 |
| C00117    | Jagdish Maharaj        | UHNI    | Ayushman Chander  |       46.5 |  1 191.9 |
| C02781    | Shivani Nazareth       | UHNI    | Fariq Kaul        |       53.3 |  1 050.3 |
| C04774    | Alexander Nath         | UHNI    | Udant Dewan       |       40.9 |    813.8 |
| C03751    | Ekaraj De              | HNI     | Tripti Yadav      |       44.1 |    460.9 |
| C01238    | Bachittar Kade         | HNI     | Gagan Sami        |       42.5 |    446.0 |
| C02254    | Yash Sehgal            | HNI     | Daksh Karnik      |       40.8 |    440.6 |
| C02753    | Harinakshi Chakraborty | HNI     | Ekbal Garg        |       40.7 |    410.1 |
| C04178    | Gaurav Golla           | HNI     | Lajita Mall       |       45.7 |    382.3 |
| C01037    | Harini Majumdar        | HNI     | Upadhriti Wadhwa  |       40.9 |    369.5 |

**Total flagged:** 166 Conservative clients hold > 40 % equity

---

## Q13 — Net New Assets Ranked Within Each Branch (Last 12 Months)

**Business question:** Who is winning new money, compared with peers in the same branch?

| branch    | advisor_name      | nna_cr  | rank_in_branch |
|-----------|-------------------|--------:|---------------:|
| Ahmedabad | Harini Choudhury  |   24.45 |              1 |
| Ahmedabad | Advay Contractor  |   13.81 |              2 |
| Ahmedabad | Aarush Lall       |    6.99 |              3 |
| Ahmedabad | Yashica Cherian   |    2.16 |              4 |
| Ahmedabad | Radhika Dugar     |   -6.57 |              5 |
| Bengaluru | Hemangini Lalla   |   16.13 |              1 |
| Bengaluru | Tripti Yadav      |   15.27 |              2 |
| Bengaluru | Kritika Brar      |    0.21 |              3 |
| Bengaluru | Janaki Handa      |   -0.59 |              4 |
| Bengaluru | Lajita Chatterjee |  -26.44 |              5 |
| Chennai   | Tara Dhar         |   28.90 |              1 |
| Chennai   | Simon Tata        |   14.31 |              2 |
| Chennai   | Liam Koshy        |    9.09 |              3 |
| Chennai   | Dominic Kakar     |    7.23 |              4 |
| Chennai   | Priya Rastogi     |    0.45 |              5 |
| Delhi NCR | Arunima Dugal     |   28.19 |              1 |
| Delhi NCR | Nathaniel Sami    |   26.18 |              2 |
| Delhi NCR | Rushil Saini      |   19.10 |              3 |
| Delhi NCR | Gayathri Chaudry  |   17.96 |              4 |
| Delhi NCR | Saumya Mall       |   13.89 |              5 |
| Hyderabad | Diya Rattan       |   21.09 |              1 |
| Hyderabad | Ekbal Garg        |   15.42 |              2 |
| Hyderabad | Daksh Karnik      |   14.91 |              3 |
| Hyderabad | Nihal Shere       |    2.15 |              4 |
| Hyderabad | Anamika Kanda     |  -12.97 |              5 |
| Kolkata   | Devansh Rajan     |   14.58 |              1 |
| Kolkata   | Upadhriti Wadhwa  |    8.96 |              2 |
| Kolkata   | Gavin Batta       |    8.30 |              3 |
| Kolkata   | Michael Dutta     |    2.33 |              4 |
| Kolkata   | Theodore Devi     |    1.68 |              5 |
| Mumbai    | Udant Dewan       |   53.43 |              1 |
| Mumbai    | Aryan Maharaj     |   27.29 |              2 |
| Mumbai    | Viraj Tiwari      |   15.48 |              3 |
| Mumbai    | Ayushman Chander  |    8.77 |              4 |
| Mumbai    | Gagan Sami        |    1.17 |              5 |
| Pune      | Chakradev Kari    |   57.53 |              1 |
| Pune      | Lajita Mall       |   52.50 |              2 |
| Pune      | Janya Gaba        |   19.16 |              3 |
| Pune      | Fariq Kaul        |    7.53 |              4 |
| Pune      | Isha Kadakia      |    2.75 |              5 |

---

## Q14 — Monthly Churn Rate by Risk Profile

**Business question:** Did churn change when markets fell, and which risk-profile clients reacted?

| month_start | clients_at_start | churned | aggressive_pct | moderate_pct | conservative_pct |
|-------------|----------------:|--------:|---------------:|-------------:|-----------------:|
| 2024-01-01  |           4 243 |      19 |           0.29 |         0.51 |             0.47 |
| 2024-02-01  |           4 254 |      18 |           0.29 |         0.41 |             0.55 |
| 2024-03-01  |           4 262 |      25 |           0.58 |         0.46 |             0.79 |
| 2024-04-01  |           4 272 |      30 |           0.57 |         0.87 |             0.55 |
| 2024-05-01  |           4 272 |      17 |           0.57 |         0.41 |             0.24 |
| 2024-06-01  |           4 293 |      22 |           0.38 |         0.66 |             0.39 |
| 2024-07-01  |           4 292 |      20 |           0.67 |         0.41 |             0.39 |
| 2024-08-01  |           4 306 |      23 |           0.67 |         0.46 |             0.54 |
| 2024-09-01  |           4 316 |      25 |           0.19 |         0.66 |             0.78 |
| 2024-10-01  |           4 334 |      28 |           0.66 |         0.71 |             0.54 |
| 2024-11-01  |           4 332 |      26 |           0.56 |         0.56 |             0.70 |
| 2024-12-01  |           4 333 |      10 |           0.19 |         0.20 |             0.31 |
| 2025-01-01  |           4 349 |      24 |           0.47 |         0.45 |             0.77 |
| 2025-02-01  |           4 358 |      25 |           0.56 |         0.45 |             0.77 |
| 2025-03-01  |           4 352 |      27 |           0.65 |         0.75 |             0.39 |
| 2025-04-01  |           4 363 |      34 |           1.40 |         0.50 |             0.69 |
| 2025-05-01  |           4 363 |      29 |           1.61 |         0.50 |             0.15 |
| 2025-06-01  |           4 371 |      27 |           1.15 |         0.50 |             0.38 |
| 2025-07-01  |           4 391 |      34 |           1.82 |         0.35 |             0.60 |
| 2025-08-01  |           4 394 |      21 |           0.19 |         0.44 |             0.75 |
| 2025-09-01  |           4 407 |      25 |           0.48 |         0.59 |             0.60 |
| 2025-10-01  |           4 406 |      22 |           0.39 |         0.59 |             0.45 |
| 2025-11-01  |           4 417 |      26 |           0.77 |         0.59 |             0.45 |
| 2025-12-01  |           4 414 |      24 |           0.48 |         0.54 |             0.60 |

