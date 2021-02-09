# CSPM
 CSPM (Compressing Star Pat-tern Miner) aims at finding star patterns in attributed graph. It identifies star-shaped attributepatterns and provides a good compression according to the min-imum description length principle. By using the concept of con-ditional entropy, the algorithm finds patterns representing strong relationships between node attributes.
 
 ### How to run?
 `pythono main.py --dataset --slim --method`
 
 * Dataset: DBLP-T0 / DBLP-Trend / USFlight
 * Slim: 1-using slim as the first step; others-without slim
 * Method: CSPM-Basic / CSPM-Partial
 
