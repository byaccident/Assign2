## The following functions cache the inverse for a matrix 'x', and store for later retrieval to reduce repeat calculations

## The following function makes a cache of the argument 'x', a matrix

makeCacheMatrix <- function(x = matrix()) {
  mInv<-NULL
  set<-function(y){
    x<<-y
    mInv<<-NULL
  }
  get<-function() x
  setmatrix<-function(solve) mInv<<- solve
  getmatrix<-function() mInv
  list(set=set, get=get,
       setmatrix=setmatrix,
       getmatrix=getmatrix)
}


## The following function solves for the inverse of the matrix supplied in cacheMatrix and retrieves this value 



cacheSolve <- function(x=matrix(), ...) {
  mInv<-x$getmatrix()
  if(!is.null(mInv)){
    message("getting cached data")
    return(mInv)
  }
  matrix<-x$get()
  mInv<-solve(matrix, ...)
  x$setmatrix(mInv)
  mInv
}