lolrly<-function(probability, size){#I cannot believe im writing this function
  vals = array()
  ret = array()
  vals = runif(size)
  for(i in 1:size){
    if(vals[i]<=probability){
      ret[i] = TRUE
    }else{
      ret[i] = FALSE
    }
  }  
  return(ret)
}