MODULE ImageDraw
  ! Generated 2026-10-06 14:54 for ABB GoFa CRB 15000-5/0.95: 4 strokes
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
    MoveL Offs(pOrigin,63.0,137.1,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,63.0,137.1,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,59.5,134.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,59.5,46.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,60.7,45.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,61.8,45.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,63.0,44.1,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,185.9,44.1,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,189.3,46.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,189.3,134.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,188.2,135.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,187.0,135.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,185.9,137.1,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,63.0,137.1,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,63.0,137.1,15.0),vApproach,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,65.3,134.8,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,65.3,134.8,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,183.6,134.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,187.0,131.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,187.0,49.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,183.6,46.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,65.3,46.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,61.8,49.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,61.8,131.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,65.3,134.8,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,65.3,134.8,15.0),vApproach,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,66.4,131.4,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,66.4,131.4,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,65.3,130.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,65.3,50.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,66.4,49.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,182.4,49.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,183.6,50.9,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,183.6,130.2,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,182.4,131.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,66.4,131.4,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,66.4,131.4,15.0),vApproach,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,69.9,129.1,15.0),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,69.9,129.1,0.0),vApproach,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,179.0,129.1,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,181.3,126.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,181.3,54.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,179.0,52.1,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,69.9,52.1,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,67.6,54.4,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,67.6,126.8,0.0),vDraw,z1,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,69.9,129.1,0.0),vDraw,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,69.9,129.1,15.0),vApproach,z5,tPen\WObj:=wPaper;
  ENDPROC

ENDMODULE