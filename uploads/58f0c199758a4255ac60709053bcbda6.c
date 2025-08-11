#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
/* ==============================TUTORIAL==============================
 *
 *   write a program to do the following 
 *
 *   - read an array
 *   - display the array 
 *   - insert a given element at a given position in the array 
 *   - delete an element from a given positon in the array 
 *   - delete the given element from the array 
 *   - search for a given element in the array 
 *
 *
 *   menu driven program with functional programming 
 * */



int * createArray(size_t size){
  int * array=(int *)malloc((100)*sizeof(int));
  if(array==NULL){
	 perror("memory allocation failed");
  }
  int * writer = array;
  while((writer - array) < size){
	 printf("enter the element: ");
	 scanf("%d",writer);
	 writer++;
  }
  return array;
}

void displayArray(int * array,int size){
  int * mover=array;

  printf("[");
  while(mover - array < size){
	  printf("%d",*mover);
	  if(mover-array<size-1) printf(",");
	  mover++;
  }
  printf("] \n");
}

void insertElement(int * array , int * size , int value, int index){
  if(index > *size) {
	 perror("insertion at invalid index");
	 return ;
  }
  int * mover=array;
  while( mover - array < *size ) mover++;
  while(mover-array!=index){
	  *mover=*(mover-1);
	  mover--;
  }
  *mover=value;
  *size+=1;
}
void deleteElementAtIndex(int * array, int *  size,int index){
  int * mover;
  mover+=index;
  while(mover-array < *size){
	 *(mover)=*(mover+1);
	 mover+=1;
  }
  *size-=1;
}

int searchElement(int * array, int size, int value){
    //implementing basic serarching 
	 int * mover= array;
	 while( mover - array < size ) {
		  if(*mover == value) return mover - array;
		  mover++;
	 }
}

void deleteElementByValue(int * array, int * size, int value){
  int index=searchElement(array,*size,value);
  if( index==-1) perror("element not found");
  deleteElementAtIndex(array,size,index);
}

void  displayMenu(int * array,int size){
  printf(" -- menu --- \n 1) createArray \n 2) insertElement \n 3) displayArray \n 4) deleteElementAtIndex \n 5) deleteElementByValue \n 6) serachElement \n 7) exit \n");
 
 }

int main(void){
  int * array;
  int size;
  int looping=1;
while(looping){
  displayMenu(array,size);
 int choice;
 printf("enter your choice : ");
  scanf("%d",&choice);
  switch(choice){
	 case 1:
		printf("enter the size of the array: ");
		scanf("%d",&size);
		array = createArray(size);
		break;
	 case 2:
		int value,index;
		printf("enter the value to be inserted");
		scanf("%d",&value);
		printf("enter the postion to be inserted to:");
		scanf("%d",&index);
		insertElement(array,&size,value,index);
		break;
	 case 3:
		displayArray(array,size);
		break;
	 case 4:
		int inx;
		printf("enter the index of element to be deleted :");
		scanf("%d",&inx);
		deleteElementAtIndex(array,&size,inx);
		break;
	 case 5:
		int val;
		printf("enter a value:");
		scanf("%d",&val);
      deleteElementByValue(array,&size,val);
		break;
	 case 6:
	 	int vals;
		printf("enter a value:");
		scanf("%d",&vals);
		int found =searchElement(array,size,vals);
		if(found==-1) printf("element wasnt found \n");
		printf("element found at index %d",found);
		break;
	 case 7:
		looping=0;
		break;
  }

}

	return 0;
}
