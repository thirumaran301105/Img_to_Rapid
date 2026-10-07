MODULE ImageDraw
  ! Generated 2026-10-06 14:54 for ABB GoFa CRB 15000-5/0.95: 2 strokes
  PERS tooldata tPen:=[TRUE,[[0,0,120.0],[1,0,0,0]],[0.3,[0,0,60.0],[1,0,0,0],0,0,0]];
  PERS wobjdata wPaper:=[FALSE,TRUE,"",[[350,-90,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
  CONST robtarget pOrigin:=[[0,0,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
  CONST jointtarget jHome:=[[0,0,0,0,30,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
  CONST speeddata vDraw:=[40,100,5000,1000];
  CONST speeddata vApproach:=[20,100,5000,1000];
  CONST speeddata vTravel:=[200,200,5000,1000];

  PROC DrawImage()
    ConfL\Off;
    ConfJ\Off;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tPen;
    Part1;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tPen;
  ENDPROC

  PROC Part1()
    MoveL Offs(pOrigin,64.1,135.9,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,64.1,135.9,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,60.7,133.6,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,60.7,47.5,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,61.8,46.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,63.0,46.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,64.1,45.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,184.7,45.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,188.2,47.5,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,188.2,133.6,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,187.0,134.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,185.9,134.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,184.7,135.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,64.1,135.9,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,64.1,135.9,15.0),vApproach,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,68.7,130.2,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,68.7,130.2,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,180.1,130.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,182.4,127.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,182.4,53.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,180.1,50.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,68.7,50.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,66.4,53.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,66.4,127.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,68.7,130.2,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,68.7,130.2,15.0),vApproach,z5,tPen\WObj:=wPaper;
  ENDPROC

ENDMODULE