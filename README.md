# CSPM
We propose a parameter-free algorithm named **CSPM (Compressing Star Pattern Miner)** which identifies star-shaped patterns that indicate strong correlations among attributes via the concept of conditional entropy and minimum description length principle.  Experiments performed on several benchmark databases show that CSPM reveals insightful and interpretable patterns and is efficient in runtime. Moreover, quantitative evaluations on two different real-world applications show the broader applicability of CSPM as it successfully boosts the accuracy of graph attribute completion models and uncovers the correlated patterns of telecommunication alarms.
 
 ### How to run?
 `python main.py --dataset --slim --method`
 
 * Dataset: DBLP-T0 / DBLP-Trend / USFlight
 * Slim: '1'-using slim as the first step; others-without slim
 * Method: CSPM-Basic / CSPM-Partial
 
