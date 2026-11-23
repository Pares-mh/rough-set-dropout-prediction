# Results summary

Data: data.csv (n=4424), 5x10 stratified CV, class counts {'Graduate': 2209, 'Dropout': 1421, 'Enrolled': 794}

## Metrics (mean ± SD)

|                                       | accuracy      | balanced_accuracy   | macro_f1      | mcc           | recall_Dropout   | recall_Enrolled   | recall_Graduate   |
|:--------------------------------------|:--------------|:--------------------|:--------------|:--------------|:-----------------|:------------------|:------------------|
| ('all', 'DecisionTree')               | 0.665 ± 0.02  | 0.597 ± 0.022       | 0.596 ± 0.022 | 0.456 ± 0.031 | 0.692 ± 0.037    | 0.332 ± 0.051     | 0.768 ± 0.031     |
| ('all', 'NaiveBayes')                 | 0.68 ± 0.023  | 0.621 ± 0.023       | 0.62 ± 0.024  | 0.481 ± 0.035 | 0.709 ± 0.039    | 0.385 ± 0.049     | 0.768 ± 0.033     |
| ('all', 'RS-EF')                      | 0.629 ± 0.06  | 0.485 ± 0.07        | 0.443 ± 0.086 | 0.373 ± 0.114 | 0.491 ± 0.229    | 0.034 ± 0.093     | 0.931 ± 0.096     |
| ('all', 'RS-EF-class-aware')          | 0.663 ± 0.036 | 0.587 ± 0.049       | 0.579 ± 0.06  | 0.457 ± 0.052 | 0.648 ± 0.109    | 0.319 ± 0.171     | 0.795 ± 0.095     |
| ('all', 'RS-EF-class-aware-k2')       | 0.67 ± 0.041  | 0.547 ± 0.05        | 0.513 ± 0.061 | 0.453 ± 0.068 | 0.626 ± 0.221    | 0.12 ± 0.166      | 0.896 ± 0.045     |
| ('all', 'RS-EF-class-aware-k6')       | 0.651 ± 0.055 | 0.565 ± 0.064       | 0.551 ± 0.083 | 0.437 ± 0.075 | 0.604 ± 0.152    | 0.272 ± 0.191     | 0.818 ± 0.138     |
| ('all', 'RS-EF-classic')              | 0.628 ± 0.022 | 0.518 ± 0.023       | 0.517 ± 0.025 | 0.367 ± 0.04  | 0.549 ± 0.052    | 0.157 ± 0.042     | 0.849 ± 0.023     |
| ('all', 'RS-EF-pruned')               | 0.661 ± 0.03  | 0.514 ± 0.034       | 0.47 ± 0.034  | 0.434 ± 0.052 | 0.614 ± 0.14     | 0.0 ± 0.0         | 0.928 ± 0.061     |
| ('all', 'RS-EF-pruned-bal')           | 0.657 ± 0.028 | 0.516 ± 0.035       | 0.468 ± 0.033 | 0.428 ± 0.05  | 0.654 ± 0.159    | 0.0 ± 0.0         | 0.894 ± 0.076     |
| ('all', 'RS-MDLP')                    | 0.614 ± 0.047 | 0.482 ± 0.058       | 0.443 ± 0.071 | 0.357 ± 0.082 | 0.489 ± 0.229    | 0.065 ± 0.122     | 0.892 ± 0.126     |
| ('all', 'RS-MDLP-class-aware')        | 0.647 ± 0.045 | 0.578 ± 0.059       | 0.57 ± 0.069  | 0.435 ± 0.065 | 0.618 ± 0.127    | 0.341 ± 0.165     | 0.775 ± 0.117     |
| ('all', 'RS-MDLP-pruned')             | 0.658 ± 0.028 | 0.509 ± 0.031       | 0.468 ± 0.031 | 0.426 ± 0.05  | 0.584 ± 0.117    | 0.001 ± 0.005     | 0.941 ± 0.047     |
| ('all', 'RS-MDLP-pruned-bal')         | 0.659 ± 0.029 | 0.511 ± 0.032       | 0.469 ± 0.031 | 0.429 ± 0.051 | 0.593 ± 0.122    | 0.001 ± 0.005     | 0.938 ± 0.049     |
| ('all', 'RandomForest')               | 0.744 ± 0.018 | 0.64 ± 0.023        | 0.645 ± 0.027 | 0.573 ± 0.032 | 0.744 ± 0.039    | 0.258 ± 0.052     | 0.919 ± 0.019     |
| ('no_finance', 'DecisionTree')        | 0.639 ± 0.021 | 0.568 ± 0.023       | 0.567 ± 0.023 | 0.413 ± 0.032 | 0.65 ± 0.04      | 0.304 ± 0.056     | 0.752 ± 0.026     |
| ('no_finance', 'NaiveBayes')          | 0.656 ± 0.023 | 0.592 ± 0.025       | 0.592 ± 0.025 | 0.439 ± 0.036 | 0.665 ± 0.04     | 0.352 ± 0.055     | 0.759 ± 0.032     |
| ('no_finance', 'RS-EF')               | 0.602 ± 0.057 | 0.47 ± 0.079        | 0.425 ± 0.101 | 0.324 ± 0.115 | 0.413 ± 0.246    | 0.088 ± 0.17      | 0.909 ± 0.086     |
| ('no_finance', 'RS-EF-class-aware')   | 0.653 ± 0.034 | 0.58 ± 0.032        | 0.574 ± 0.037 | 0.44 ± 0.045  | 0.664 ± 0.075    | 0.304 ± 0.144     | 0.771 ± 0.075     |
| ('no_finance', 'RS-EF-classic')       | 0.627 ± 0.023 | 0.517 ± 0.026       | 0.513 ± 0.028 | 0.365 ± 0.044 | 0.552 ± 0.083    | 0.15 ± 0.043      | 0.847 ± 0.03      |
| ('no_finance', 'RS-EF-pruned')        | 0.654 ± 0.025 | 0.509 ± 0.026       | 0.466 ± 0.027 | 0.418 ± 0.046 | 0.613 ± 0.112    | 0.001 ± 0.006     | 0.914 ± 0.065     |
| ('no_finance', 'RS-EF-pruned-bal')    | 0.655 ± 0.024 | 0.511 ± 0.026       | 0.467 ± 0.027 | 0.42 ± 0.045  | 0.619 ± 0.112    | 0.001 ± 0.006     | 0.913 ± 0.066     |
| ('no_finance', 'RS-MDLP')             | 0.618 ± 0.063 | 0.494 ± 0.067       | 0.448 ± 0.084 | 0.361 ± 0.115 | 0.542 ± 0.282    | 0.077 ± 0.137     | 0.862 ± 0.121     |
| ('no_finance', 'RS-MDLP-class-aware') | 0.643 ± 0.031 | 0.577 ± 0.027       | 0.572 ± 0.029 | 0.43 ± 0.04   | 0.652 ± 0.115    | 0.33 ± 0.122      | 0.749 ± 0.08      |
| ('no_finance', 'RS-MDLP-pruned')      | 0.65 ± 0.024  | 0.501 ± 0.026       | 0.461 ± 0.023 | 0.413 ± 0.045 | 0.561 ± 0.102    | 0.002 ± 0.005     | 0.941 ± 0.048     |
| ('no_finance', 'RS-MDLP-pruned-bal')  | 0.651 ± 0.023 | 0.503 ± 0.027       | 0.463 ± 0.023 | 0.416 ± 0.045 | 0.57 ± 0.113     | 0.002 ± 0.005     | 0.937 ± 0.052     |
| ('no_finance', 'RandomForest')        | 0.721 ± 0.015 | 0.612 ± 0.018       | 0.614 ± 0.021 | 0.533 ± 0.027 | 0.702 ± 0.039    | 0.221 ± 0.043     | 0.913 ± 0.019     |

## Rule quality

|                                       |   n_rules |   n_rules_raw |   mean_rule_length |   mean_support |   coverage |   certain_coverage |   reduct_size |   boundary_train |   rules_Dropout |   rules_Enrolled |   rules_Graduate |
|:--------------------------------------|----------:|--------------:|-------------------:|---------------:|-----------:|-------------------:|--------------:|-----------------:|----------------:|-----------------:|-----------------:|
| ('all', 'RS-EF')                      |     19.16 |         19.34 |              1.569 |        472.668 |      1     |              0.727 |          2.86 |            0.272 |            7.34 |             5.36 |             6.46 |
| ('all', 'RS-EF-class-aware')          |     66.32 |        115.6  |              2.539 |        191.699 |      0.965 |              0.8   |          3.54 |            0.142 |           28.52 |            15.56 |            22.24 |
| ('all', 'RS-EF-class-aware-k2')       |      8.4  |         17.36 |              1.811 |        818.239 |      0.998 |              0.929 |          2.94 |            0.004 |            4.08 |             1.5  |             2.82 |
| ('all', 'RS-EF-class-aware-k6')       |     62.96 |        122.78 |              2.157 |        191.631 |      0.932 |              0.788 |          2.94 |            0.097 |           25.86 |            15.44 |            21.66 |
| ('all', 'RS-EF-classic')              |   1352.02 |       1352.02 |              4.494 |          4.272 |      0.776 |              0.593 |         13.12 |            0     |          433.8  |           389.2  |           529.02 |
| ('all', 'RS-EF-pruned')               |      7.98 |         19.34 |              1.901 |        468.921 |      0.747 |              0.726 |          2.86 |            0.272 |            4.88 |             0    |             3.1  |
| ('all', 'RS-EF-pruned-bal')           |      7.98 |         19.34 |              1.901 |        468.921 |      0.747 |              0.726 |          2.86 |            0.272 |            4.88 |             0    |             3.1  |
| ('all', 'RS-MDLP')                    |     27.48 |         29    |              1.482 |        352.363 |      1     |              0.725 |          2.38 |            0.276 |            9.94 |             6.98 |            10.56 |
| ('all', 'RS-MDLP-class-aware')        |     67.14 |        120.02 |              2.294 |        171.864 |      0.97  |              0.781 |          3.06 |            0.165 |           31.34 |            17.8  |            18    |
| ('all', 'RS-MDLP-pruned')             |     10.48 |         29    |              1.695 |        430.909 |      0.756 |              0.724 |          2.38 |            0.276 |            5.38 |             0.14 |             4.96 |
| ('all', 'RS-MDLP-pruned-bal')         |     10.48 |         29    |              1.695 |        430.909 |      0.756 |              0.724 |          2.38 |            0.276 |            5.38 |             0.14 |             4.96 |
| ('no_finance', 'RS-EF')               |     45.9  |         46.58 |              1.756 |        326.379 |      1     |              0.582 |          2.7  |            0.418 |           16.94 |            12.88 |            16.08 |
| ('no_finance', 'RS-EF-class-aware')   |     56.78 |        119.62 |              1.988 |        233.086 |      0.956 |              0.815 |          2.58 |            0.11  |           23.12 |            13.78 |            19.88 |
| ('no_finance', 'RS-EF-classic')       |   1764.18 |       2214.92 |              4.43  |          4.004 |      0.824 |              0.583 |         12.16 |            0     |          600.94 |           389.86 |           773.38 |
| ('no_finance', 'RS-EF-pruned')        |     12.58 |         46.58 |              1.972 |        432.688 |      0.708 |              0.579 |          2.7  |            0.418 |            7.28 |             0.18 |             5.12 |
| ('no_finance', 'RS-EF-pruned-bal')    |     12.58 |         46.58 |              1.972 |        432.688 |      0.708 |              0.579 |          2.7  |            0.418 |            7.28 |             0.18 |             5.12 |
| ('no_finance', 'RS-MDLP')             |     32.36 |         34.58 |              1.494 |        262.582 |      1     |              0.691 |          2.26 |            0.311 |           11.98 |             8.44 |            11.94 |
| ('no_finance', 'RS-MDLP-class-aware') |     67.3  |        135.16 |              1.981 |        135.676 |      0.959 |              0.776 |          2.46 |            0.152 |           32.72 |            17.24 |            17.34 |
| ('no_finance', 'RS-MDLP-pruned')      |     10.12 |         34.58 |              1.632 |        439.539 |      0.741 |              0.689 |          2.26 |            0.311 |            4.94 |             0.2  |             4.98 |
| ('no_finance', 'RS-MDLP-pruned-bal')  |     10.12 |         34.58 |              1.632 |        439.539 |      0.741 |              0.689 |          2.26 |            0.311 |            4.94 |             0.2  |             4.98 |

## Significance (rough-set vs baselines, Holm-adjusted)

| feature_set   | metric            | rough_set_model      | baseline       |   mean_diff |   wilcoxon_p |   corrected_t |   corrected_t_p |   wilcoxon_p_holm |   corrected_t_p_holm |
|:--------------|:------------------|:---------------------|:---------------|------------:|-------------:|--------------:|----------------:|------------------:|---------------------:|
| all           | macro_f1          | RS-EF                | DecisionTree   |     -0.1533 |       0      |       -4.4392 |          0.0001 |            0      |               0.0007 |
| all           | macro_f1          | RS-EF                | RandomForest   |     -0.2021 |       0      |       -6.0718 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF                | NaiveBayes     |     -0.1769 |       0      |       -5.6082 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-class-aware    | DecisionTree   |     -0.0175 |       0.1074 |       -0.7944 |          0.4308 |            0.1611 |               0.6845 |
| all           | macro_f1          | RS-EF-class-aware    | RandomForest   |     -0.0663 |       0      |       -3.0281 |          0.0039 |            0      |               0.0313 |
| all           | macro_f1          | RS-EF-class-aware    | NaiveBayes     |     -0.0411 |       0      |       -2.0036 |          0.0507 |            0      |               0.2207 |
| all           | macro_f1          | RS-EF-class-aware    | RS-EF-pruned   |      0.1089 |       0      |        4.6974 |          0      |            0      |               0.0003 |
| all           | macro_f1          | RS-EF-class-aware-k2 | DecisionTree   |     -0.0837 |       0      |       -3.5094 |          0.001  |            0      |               0.0097 |
| all           | macro_f1          | RS-EF-class-aware-k2 | RandomForest   |     -0.1325 |       0      |       -5.57   |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-class-aware-k2 | NaiveBayes     |     -0.1073 |       0      |       -4.4425 |          0.0001 |            0      |               0.0007 |
| all           | macro_f1          | RS-EF-class-aware-k6 | DecisionTree   |     -0.0453 |       0.0015 |       -1.4447 |          0.1549 |            0.0046 |               0.4647 |
| all           | macro_f1          | RS-EF-class-aware-k6 | RandomForest   |     -0.0942 |       0      |       -3.1699 |          0.0026 |            0      |               0.0237 |
| all           | macro_f1          | RS-EF-class-aware-k6 | NaiveBayes     |     -0.069  |       0      |       -2.4098 |          0.0198 |            0      |               0.1186 |
| all           | macro_f1          | RS-EF-classic        | DecisionTree   |     -0.0795 |       0      |       -6.8368 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-classic        | RandomForest   |     -0.1283 |       0      |      -11.7312 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-classic        | NaiveBayes     |     -0.1031 |       0      |       -9.1134 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-pruned         | DecisionTree   |     -0.1264 |       0      |       -8.6582 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-pruned         | RandomForest   |     -0.1752 |       0      |      -12.3411 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-pruned         | NaiveBayes     |     -0.15   |       0      |      -10.6853 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-pruned-bal     | DecisionTree   |     -0.1284 |       0      |       -8.896  |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-pruned-bal     | RandomForest   |     -0.1772 |       0      |      -12.7297 |          0      |            0      |               0      |
| all           | macro_f1          | RS-EF-pruned-bal     | NaiveBayes     |     -0.152  |       0      |      -10.9967 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP              | DecisionTree   |     -0.1536 |       0      |       -5.3028 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP              | RandomForest   |     -0.2024 |       0      |       -7.8879 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP              | NaiveBayes     |     -0.1772 |       0      |       -6.8048 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP-class-aware  | DecisionTree   |     -0.0264 |       0.0805 |       -0.959  |          0.3423 |            0.1611 |               0.6845 |
| all           | macro_f1          | RS-MDLP-class-aware  | RandomForest   |     -0.0753 |       0      |       -2.9934 |          0.0043 |            0      |               0.0313 |
| all           | macro_f1          | RS-MDLP-class-aware  | NaiveBayes     |     -0.0501 |       0      |       -2.066  |          0.0441 |            0      |               0.2207 |
| all           | macro_f1          | RS-MDLP-class-aware  | RS-MDLP-pruned |      0.1022 |       0      |        3.9484 |          0.0003 |            0      |               0.0028 |
| all           | macro_f1          | RS-MDLP-pruned       | DecisionTree   |     -0.1286 |       0      |       -9.5769 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP-pruned       | RandomForest   |     -0.1775 |       0      |      -14.5043 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP-pruned       | NaiveBayes     |     -0.1523 |       0      |      -13.8867 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP-pruned-bal   | DecisionTree   |     -0.1272 |       0      |       -9.4091 |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP-pruned-bal   | RandomForest   |     -0.176  |       0      |      -14.541  |          0      |            0      |               0      |
| all           | macro_f1          | RS-MDLP-pruned-bal   | NaiveBayes     |     -0.1508 |       0      |      -13.6981 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF                | DecisionTree   |     -0.112  |       0      |       -3.9331 |          0.0003 |            0      |               0.0037 |
| all           | balanced_accuracy | RS-EF                | RandomForest   |     -0.1551 |       0      |       -5.7097 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF                | NaiveBayes     |     -0.1355 |       0      |       -5.1713 |          0      |            0      |               0.0001 |
| all           | balanced_accuracy | RS-EF-class-aware    | DecisionTree   |     -0.0097 |       0.3673 |       -0.5283 |          0.5997 |            0.3953 |               0.8453 |
| all           | balanced_accuracy | RS-EF-class-aware    | RandomForest   |     -0.0528 |       0      |       -2.9986 |          0.0043 |            0      |               0.0383 |
| all           | balanced_accuracy | RS-EF-class-aware    | NaiveBayes     |     -0.0332 |       0      |       -1.9634 |          0.0553 |            0      |               0.2212 |
| all           | balanced_accuracy | RS-EF-class-aware    | RS-EF-pruned   |      0.0732 |       0      |        3.7139 |          0.0005 |            0      |               0.0068 |
| all           | balanced_accuracy | RS-EF-class-aware-k2 | DecisionTree   |     -0.0498 |       0      |       -2.4967 |          0.0159 |            0      |               0.0978 |
| all           | balanced_accuracy | RS-EF-class-aware-k2 | RandomForest   |     -0.093  |       0      |       -4.8095 |          0      |            0      |               0.0002 |
| all           | balanced_accuracy | RS-EF-class-aware-k2 | NaiveBayes     |     -0.0734 |       0      |       -3.6657 |          0.0006 |            0      |               0.0073 |
| all           | balanced_accuracy | RS-EF-class-aware-k6 | DecisionTree   |     -0.0324 |       0.0051 |       -1.2986 |          0.2001 |            0.0152 |               0.6004 |
| all           | balanced_accuracy | RS-EF-class-aware-k6 | RandomForest   |     -0.0755 |       0      |       -3.3089 |          0.0018 |            0      |               0.0194 |
| all           | balanced_accuracy | RS-EF-class-aware-k6 | NaiveBayes     |     -0.0559 |       0      |       -2.5495 |          0.014  |            0      |               0.0978 |
| all           | balanced_accuracy | RS-EF-classic        | DecisionTree   |     -0.0788 |       0      |       -7.1968 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-classic        | RandomForest   |     -0.122  |       0      |      -12.4898 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-classic        | NaiveBayes     |     -0.1024 |       0      |      -10.0904 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-pruned         | DecisionTree   |     -0.0829 |       0      |       -5.494  |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-pruned         | RandomForest   |     -0.126  |       0      |       -9.3282 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-pruned         | NaiveBayes     |     -0.1064 |       0      |       -7.6574 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-pruned-bal     | DecisionTree   |     -0.081  |       0      |       -5.3017 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-pruned-bal     | RandomForest   |     -0.1241 |       0      |       -9.0225 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-EF-pruned-bal     | NaiveBayes     |     -0.1045 |       0      |       -7.3211 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP              | DecisionTree   |     -0.1153 |       0      |       -4.782  |          0      |            0      |               0.0002 |
| all           | balanced_accuracy | RS-MDLP              | RandomForest   |     -0.1585 |       0      |       -7.5245 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP              | NaiveBayes     |     -0.1389 |       0      |       -6.4441 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP-class-aware  | DecisionTree   |     -0.0193 |       0.1976 |       -0.8086 |          0.4227 |            0.3953 |               0.8453 |
| all           | balanced_accuracy | RS-MDLP-class-aware  | RandomForest   |     -0.0625 |       0      |       -2.9363 |          0.005  |            0      |               0.0404 |
| all           | balanced_accuracy | RS-MDLP-class-aware  | NaiveBayes     |     -0.0429 |       0      |       -2.0901 |          0.0418 |            0      |               0.2091 |
| all           | balanced_accuracy | RS-MDLP-class-aware  | RS-MDLP-pruned |      0.0691 |       0      |        3.0759 |          0.0034 |            0      |               0.0343 |
| all           | balanced_accuracy | RS-MDLP-pruned       | DecisionTree   |     -0.0885 |       0      |       -6.668  |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP-pruned       | RandomForest   |     -0.1316 |       0      |      -11.1356 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP-pruned       | NaiveBayes     |     -0.112  |       0      |       -9.8216 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP-pruned-bal   | DecisionTree   |     -0.0864 |       0      |       -6.4355 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP-pruned-bal   | RandomForest   |     -0.1296 |       0      |      -10.9607 |          0      |            0      |               0      |
| all           | balanced_accuracy | RS-MDLP-pruned-bal   | NaiveBayes     |     -0.11   |       0      |       -9.4476 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF                | DecisionTree   |     -0.1422 |       0      |       -3.5592 |          0.0008 |            0      |               0.005  |
| no_finance    | macro_f1          | RS-EF                | RandomForest   |     -0.1886 |       0      |       -4.9648 |          0      |            0      |               0.0001 |
| no_finance    | macro_f1          | RS-EF                | NaiveBayes     |     -0.1666 |       0      |       -4.6831 |          0      |            0      |               0.0002 |
| no_finance    | macro_f1          | RS-EF-class-aware    | DecisionTree   |      0.0063 |       0.2653 |        0.4726 |          0.6386 |            0.5307 |               1      |
| no_finance    | macro_f1          | RS-EF-class-aware    | RandomForest   |     -0.0401 |       0      |       -3.2881 |          0.0019 |            0      |               0.0094 |
| no_finance    | macro_f1          | RS-EF-class-aware    | NaiveBayes     |     -0.0181 |       0.0002 |       -1.54   |          0.13   |            0.0007 |               0.39   |
| no_finance    | macro_f1          | RS-EF-class-aware    | RS-EF-pruned   |      0.1078 |       0      |        7.4706 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-classic        | DecisionTree   |     -0.0544 |       0      |       -4.5707 |          0      |            0      |               0.0003 |
| no_finance    | macro_f1          | RS-EF-classic        | RandomForest   |     -0.1008 |       0      |       -8.7031 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-classic        | NaiveBayes     |     -0.0788 |       0      |       -6.2604 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-pruned         | DecisionTree   |     -0.1015 |       0      |       -9.1889 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-pruned         | RandomForest   |     -0.1479 |       0      |      -14.1232 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-pruned         | NaiveBayes     |     -0.1259 |       0      |      -10.5018 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-pruned-bal     | DecisionTree   |     -0.1004 |       0      |       -9.169  |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-pruned-bal     | RandomForest   |     -0.1468 |       0      |      -14.1009 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-EF-pruned-bal     | NaiveBayes     |     -0.1248 |       0      |      -10.747  |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP              | DecisionTree   |     -0.1194 |       0      |       -4.0187 |          0.0002 |            0      |               0.0015 |
| no_finance    | macro_f1          | RS-MDLP              | RandomForest   |     -0.1658 |       0      |       -5.5722 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP              | NaiveBayes     |     -0.1438 |       0      |       -4.9974 |          0      |            0      |               0.0001 |
| no_finance    | macro_f1          | RS-MDLP-class-aware  | DecisionTree   |      0.0041 |       0.2653 |        0.3886 |          0.6993 |            0.5307 |               1      |
| no_finance    | macro_f1          | RS-MDLP-class-aware  | RandomForest   |     -0.0423 |       0      |       -4.0465 |          0.0002 |            0      |               0.0015 |
| no_finance    | macro_f1          | RS-MDLP-class-aware  | NaiveBayes     |     -0.0203 |       0      |       -1.8337 |          0.0728 |            0.0002 |               0.2911 |
| no_finance    | macro_f1          | RS-MDLP-class-aware  | RS-MDLP-pruned |      0.1102 |       0      |        9.5314 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP-pruned       | DecisionTree   |     -0.106  |       0      |       -9.2921 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP-pruned       | RandomForest   |     -0.1524 |       0      |      -14.7541 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP-pruned       | NaiveBayes     |     -0.1304 |       0      |      -11.3628 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP-pruned-bal   | DecisionTree   |     -0.1049 |       0      |       -9.2984 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP-pruned-bal   | RandomForest   |     -0.1513 |       0      |      -14.8916 |          0      |            0      |               0      |
| no_finance    | macro_f1          | RS-MDLP-pruned-bal   | NaiveBayes     |     -0.1293 |       0      |      -11.2795 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF                | DecisionTree   |     -0.0986 |       0      |       -3.0828 |          0.0034 |            0      |               0.0203 |
| no_finance    | balanced_accuracy | RS-EF                | RandomForest   |     -0.1423 |       0      |       -4.7723 |          0      |            0      |               0.0002 |
| no_finance    | balanced_accuracy | RS-EF                | NaiveBayes     |     -0.1222 |       0      |       -4.3909 |          0.0001 |            0      |               0.0006 |
| no_finance    | balanced_accuracy | RS-EF-class-aware    | DecisionTree   |      0.0116 |       0.0224 |        0.9667 |          0.3384 |            0.0413 |               0.7726 |
| no_finance    | balanced_accuracy | RS-EF-class-aware    | RandomForest   |     -0.032  |       0      |       -3.1349 |          0.0029 |            0      |               0.0203 |
| no_finance    | balanced_accuracy | RS-EF-class-aware    | NaiveBayes     |     -0.0119 |       0.0094 |       -1.1456 |          0.2575 |            0.0282 |               0.7726 |
| no_finance    | balanced_accuracy | RS-EF-class-aware    | RS-EF-pruned   |      0.0706 |       0      |        5.6229 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-classic        | DecisionTree   |     -0.0518 |       0      |       -4.5148 |          0      |            0      |               0.0004 |
| no_finance    | balanced_accuracy | RS-EF-classic        | RandomForest   |     -0.0954 |       0      |       -9.1689 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-classic        | NaiveBayes     |     -0.0753 |       0      |       -6.3139 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-pruned         | DecisionTree   |     -0.0589 |       0      |       -5.5306 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-pruned         | RandomForest   |     -0.1026 |       0      |      -11.2449 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-pruned         | NaiveBayes     |     -0.0825 |       0      |       -7.0227 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-pruned-bal     | DecisionTree   |     -0.0575 |       0      |       -5.4488 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-pruned-bal     | RandomForest   |     -0.1012 |       0      |      -11.2306 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-EF-pruned-bal     | NaiveBayes     |     -0.0811 |       0      |       -7.1909 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-MDLP              | DecisionTree   |     -0.0746 |       0      |       -3.0972 |          0.0032 |            0      |               0.0203 |
| no_finance    | balanced_accuracy | RS-MDLP              | RandomForest   |     -0.1182 |       0      |       -5.0951 |          0      |            0      |               0.0001 |
| no_finance    | balanced_accuracy | RS-MDLP              | NaiveBayes     |     -0.0981 |       0      |       -4.3208 |          0.0001 |            0      |               0.0007 |
| no_finance    | balanced_accuracy | RS-MDLP-class-aware  | DecisionTree   |      0.0089 |       0.0207 |        0.9    |          0.3725 |            0.0413 |               0.7726 |
| no_finance    | balanced_accuracy | RS-MDLP-class-aware  | RandomForest   |     -0.0347 |       0      |       -3.7766 |          0.0004 |            0      |               0.0034 |
| no_finance    | balanced_accuracy | RS-MDLP-class-aware  | NaiveBayes     |     -0.0146 |       0.0023 |       -1.4036 |          0.1668 |            0.0091 |               0.667  |
| no_finance    | balanced_accuracy | RS-MDLP-class-aware  | RS-MDLP-pruned |      0.0761 |       0      |        6.1126 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-MDLP-pruned       | DecisionTree   |     -0.0672 |       0      |       -5.4616 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-MDLP-pruned       | RandomForest   |     -0.1108 |       0      |      -10.6542 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-MDLP-pruned       | NaiveBayes     |     -0.0907 |       0      |       -7.3251 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-MDLP-pruned-bal   | DecisionTree   |     -0.0654 |       0      |       -5.2686 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-MDLP-pruned-bal   | RandomForest   |     -0.109  |       0      |      -10.3472 |          0      |            0      |               0      |
| no_finance    | balanced_accuracy | RS-MDLP-pruned-bal   | NaiveBayes     |     -0.0889 |       0      |       -7.0178 |          0      |            0      |               0      |

## Certain-rule three-way decision (finance included)

| model                |   coverage |   accuracy |
|:---------------------|-----------:|-----------:|
| RS-EF                |      0.727 |      0.777 |
| RS-EF-class-aware    |      0.8   |      0.756 |
| RS-EF-class-aware-k2 |      0.929 |      0.716 |
| RS-EF-class-aware-k6 |      0.788 |      0.752 |
| RS-EF-classic        |      0.593 |      0.675 |
| RS-EF-pruned         |      0.726 |      0.778 |
| RS-EF-pruned-bal     |      0.726 |      0.778 |
| RS-MDLP              |      0.725 |      0.772 |
| RS-MDLP-class-aware  |      0.781 |      0.764 |
| RS-MDLP-pruned       |      0.724 |      0.773 |
| RS-MDLP-pruned-bal   |      0.724 |      0.773 |

## Dropout early-warning regions (alpha=0.6, beta=0.3)

| model             |   accept_share |   defer_share |   reject_share |   accept_precision |   reject_npv |   dropouts_flagged |   dropouts_deferred |   dropouts_missed |   dropout_rate_in_defer |
|:------------------|---------------:|--------------:|---------------:|-------------------:|-------------:|-------------------:|--------------------:|------------------:|------------------------:|
| DecisionTree      |          0.272 |         0.102 |          0.626 |              0.748 |        0.867 |              0.634 |               0.107 |             0.26  |                   0.337 |
| RS-EF-class-aware |          0.266 |         0.107 |          0.628 |              0.741 |        0.863 |              0.604 |               0.119 |             0.277 |                   0.416 |
| RandomForest      |          0.213 |         0.159 |          0.629 |              0.896 |        0.905 |              0.593 |               0.22  |             0.187 |                   0.446 |

## Most common granulation choice per fold

|                                    |   granule_min |   beta |
|:-----------------------------------|--------------:|-------:|
| ('all', 'EF')                      |            10 |   0.7  |
| ('all', 'EF-class-aware')          |             5 |   0.4  |
| ('all', 'MDLP')                    |            10 |   0.6  |
| ('all', 'MDLP-class-aware')        |             5 |   0.25 |
| ('no_finance', 'EF')               |            10 |   0.8  |
| ('no_finance', 'EF-class-aware')   |             5 |   0.25 |
| ('no_finance', 'MDLP')             |            10 |   0.6  |
| ('no_finance', 'MDLP-class-aware') |             5 |   0.25 |