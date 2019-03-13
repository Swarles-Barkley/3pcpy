avgFailChance = 0.01
permaFailChance = 0.01
times = array()
failures = array()
timeout = 200 #ms
simnum = 500
phasethresh1 = 0
phasethresh2 = 2
phasethresh3 = 10
phaseretry = 0
nodes = 100
quor = 0.02
results = matrix(0,nrow = simnum, ncol = 10)
results2 = matrix(0,nrow = simnum, ncol = 10)
results3 = matrix(0,nrow = simnum, ncol = 10)

for(i in 1:10){
  nodes = 25*i
  nodeWeights = rep(1,nodes)
for(j in 1:simnum){
    permaFailures = lolrly(permaFailChance, nodes)
    times = rexp(nodes, 0.5) # 1/0.05=20
    threshold = ceiling(nodes*quor) #quorum level
    #if(threshold<nodes*quor){
    #  threshold = threshold+1
    #}
    threshold = threshold+1
    phaseretry = 0
    tmp = phasesuccess(times, timeout, avgFailChance, permaFailures, threshold,nodeWeights)
    while(isFALSE(tmp) && phaseretry<phasethresh1){
      failures = lolrly(avgFailChance, nodes)
      times = rexp(nodes, 0.5) # 1/0.05=20
      
      tmp = phasesuccess(times, timeout, avgFailChance, permaFailures, threshold,nodeWeights)
      phaseretry = phaseretry + 1
    }
    results[j,i] = tmp
    
    phaseretry = 0
    tmp = phasesuccess(times, timeout, avgFailChance, permaFailures, threshold,nodeWeights)
    while(isFALSE(tmp) && phaseretry<phasethresh2){
      failures = lolrly(avgFailChance, nodes)
      times = rexp(nodes, 0.5) # 1/0.05=20
      
      tmp = phasesuccess(times, timeout, avgFailChance, permaFailures, threshold,nodeWeights)
      phaseretry = phaseretry + 1
    }
    results2[j,i] = tmp
    
    phaseretry = 0
    tmp = phasesuccess(times, timeout, avgFailChance, permaFailures, threshold,nodeWeights)
    while(isFALSE(tmp) && phaseretry<phasethresh3){
      failures = lolrly(avgFailChance, nodes)
      times = rexp(nodes, 0.5) # 1/0.05=20
      
      tmp = phasesuccess(times, timeout, avgFailChance, permaFailures, threshold,nodeWeights)
      phaseretry = phaseretry + 1
    }
    results3[j,i] = tmp
  }
}
x = seq(25, 250, by=25)
y = rep(0,10)
y2 = rep(0,10)
y3 = rep(0,10)
for(i in 1:10){
  y[i] = mean(results[,i])*100
}
plot(x,y, xlab="# nodes", ylab="% success", main="98% Quorum with 2% message failure", ylim=c(0,100), xlim=c(0,250), pch=0, col="red")
for(i in 1:10){
  y2[i] = mean(results2[,i])*100
}
for(i in 1:10){
  y3[i] = mean(results3[,i])*100
}
points(x,y2, pch=0)
points(x,y3, col="blue", pch=0)
# fit a line to the points
myline.fit <- lm(y ~ x)
myline2.fit <-lm(y2 ~ x)
myline3.fit <-lm(y3 ~ x)
# get information about the fit
#summary(myline.fit)

# draw the fit line on the plot
abline(myline.fit, col = "red")
abline(myline2.fit)
abline(myline3.fit, col = "blue")

legend(125, 20, legend=c("No retries", "2 retries", "10 retries"),
       col=c("red", "black", "blue"), lty=1:3, cex=0.8)