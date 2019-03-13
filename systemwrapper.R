avgFailChance = 0.02
times = array()
failures = array()
timeout = 200 #ms
simnum = 500
phasethresh = 10
phaseretry = 0
nodes = 100
quor = 0.02
results = matrix(0,nrow = simnum, ncol = 10)
results2 = matrix(0,nrow = simnum, ncol = 10)
results3 = matrix(0,nrow = simnum, ncol = 10)

for(i in 1:10){
  nodes = 25*i
  for(j in 1:simnum){
    results[j,i] = systemsuccess(1,200,avgFailChance, ceiling(quor*nodes),nodes,0)
    results2[j,i] = systemsuccess(1,200,avgFailChance, ceiling(quor*nodes),nodes,2)
    results3[j,i] = systemsuccess(1,200,avgFailChance, ceiling(quor*nodes),nodes,10)
  }
}

x = seq(25, 250, by=25)
y = rep(0,10)
y2 = rep(0,10)
y3 = rep(0,10)
for(i in 1:10){
  y[i] = mean(results[,i])*100
}
plot(x,y, xlab="# nodes", ylab="% success", main="Full System: 70% Quorum with 30%", ylim=c(0,100), xlim=c(0,250), pch=0, col="red")
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