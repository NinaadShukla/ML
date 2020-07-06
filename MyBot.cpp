#include "Othello.h"
#include "OthelloBoard.h"
#include "OthelloPlayer.h"
#include <cstdlib>
using namespace std;
using namespace Desdemona;

class MyBot: public OthelloPlayer
{
    public:
        MyBot( Turn turn );
	virtual Move play( const OthelloBoard& board );
        virtual int mini(const OthelloBoard& board, int ply, int max_min, int min_max);
        virtual int maxi(const OthelloBoard& board, int ply, int max_min, int min_max);
        int move_num = 0;
        Turn my_color;
    private:
};

MyBot::MyBot( Turn turn )
    : OthelloPlayer( turn )
{
}

Move MyBot::play( const OthelloBoard& board )
{
  move_num++;
  int ply=2;
  if(move_num==1)my_color = turn;
    list<Move> moves = board.getValidMoves( turn );
    list<Move>::iterator it = moves.begin();
    int max = -100;
    int a;
    Move next_move = *it;
    for(int i=1; i < moves.size(); it++, i++){
      Turn trn = turn;
      OthelloBoard my_board = board;
      my_board.makeMove(trn,*it);
      a = mini(my_board,ply,max,100);
      if(a>max){
        max = a;
        next_move = *it;
      }
    }
    return next_move;
}
extern "C" {
    OthelloPlayer* createBot( Turn turn )
    {
        return new MyBot( turn );
    }

    void destroyBot( OthelloPlayer* bot )
    {
        delete bot;
    }
}
int MyBot::maxi(const OthelloBoard& board, int ply, int min, int max){
  if(ply == 0){
    OthelloBoard my_board = board;
    Turn turn_b = other(turn);
    int i,j;
    int sum =0;
    if(move_num <32){
       int ar[8][8]={8,-7, 3, 3, 3, 3,-7, 8,
                    -7, -4, 2, 2, 2, 2, -4,-7,
                     3, 2, 1, 1, 1, 1, 2, 3,
                     3, 2, 1, 1, 1, 1, 2, 3,
                     3, 2, 1, 1, 1, 1, 2, 3,
                     3, 2, 1, 1, 1, 1, 2, 3,
                    -7, -4, 2, 2, 2, 2, -4,-7,
                    8,-7, 3, 3, 3, 3,-7, 8};
       for(i=0;i<8;i++){
         for(j=0;j<8;j++){
           if(board.get(i,j)==turn)
   	     sum = sum+ar[i][j];
           if(board.get(i,j)==turn_b)
	     sum = sum-ar[i][j];
         }
       }
    }
    else{
       int ar[8][8]={16, -16, 1, 1, 1, 1, -16, 16,
                    -16, -8, 0, 0, 0, 0, -8, -16,
                     1, 0, 0, 0, 0, 0, 0, 1,
                     1, 0, 0, 0, 0, 0, 0, 1,
                     1, 0, 0, 0, 0, 0, 0, 1,
                     1, 0, 0, 0, 0, 0, 0, 1,
                    -16, -8, 0, 0, 0, 0, -8, -16,
                    16, -16, 1, 1, 1, 1, -16, 16};
       for(i=0;i<8;i++){
         for(j=0;j<8;j++){
           if(board.get(i,j)==turn)
             sum = sum+ar[i][j];
           if(board.get(i,j)==turn_b)
             sum = sum-ar[i][j];
         }
       }
    }
    return sum;
  }
  list<Move> moves = board.getValidMoves( turn );
  list<Move>::iterator it = moves.begin();
  int a1 = min;
  int a2;
  for(int i=0; i < moves.size(); it++, i++){
    Turn t1 = turn;
    OthelloBoard my_board = board;
    my_board.makeMove(t1,*it);
    a2 = mini(my_board,ply,a1,max);
    if(a2>a1){
      a1 = a2;
      if(a1>max)
	return max;
    }
  }
  return a1;
}
int MyBot::mini(const OthelloBoard& board, int ply, int min, int max){
  Turn turn_b = (turn==RED)?BLACK:RED;
  list<Move> moves = board.getValidMoves( turn_b );
  list<Move>::iterator it = moves.begin();
  int b1 = max;
  int b2;
  for(int i=0; i < moves.size(); it++, i++){
    Turn t2 = turn_b;
    OthelloBoard my_board = board;
    my_board.makeMove(t2,*it);
    b2 = maxi(my_board,ply-1,min,b1);
    if(b2<b1){
      b1 = b2;
      if(b1<min)
	return min;
    }
  }
  return b1;
}
