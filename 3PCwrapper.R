#nodes = 10
#nodefail = 0.01
#nodezucc = 1-failprob
#syszucc = (nodezucc^nodes)^3
avgFailChance = 0.01
times = array()
failures = array()
timeout = 200 #ms
simnum = 500
results = matrix(0,nrow = simnum, ncol = 10)
for(i in 1:10){
  nodes = 25*i
  nodeWeights = rep(1,nodes)
  for(j in 1:simnum){
    #maxBackoff = 1024
    failures = lolrly(avgFailChance, nodes)
    times = rexp(nodes, 0.5) # 1/0.05=20
    threshold = as.integer(nodes*0.02) #quorum level
    threshold = threshold+1
    if(threshold<1) threshold=1
    results[j,i] = phasesuccess(times, timeout, failures,threshold,nodeWeights)
  }
}
x = seq(25, 250, by=25)
y = rep(0,10)
for(i in 1:10){
  y[i] = mean(results[,i])*100
}
plot(x,y, xlab="# nodes", ylab="% success", main="98% Quorum", ylim=c(0,100), xlim=c(0,250), pch=15, col="blue")
# fit a line to the points
myline.fit <- lm(y ~ x)

# get information about the fit
summary(myline.fit)

# draw the fit line on the plot
abline(myline.fit)

#threshold = 10
#mean(nodeWeights)
#for(i in 1:nodes){
#gen timeouts and weight nodes
#tmpProb = rexp(1, 1/avgFailChance)
#tmpProb=avgFailChance
#backoff = genTimeout(tmpProb,maxBackoff)
#if(backoff!=maxBackoff){
#  print(backoff)
#}
#weight = nodeWeighter(backoff, maxBackoff)
#nodeWeights[i] = weight
#}