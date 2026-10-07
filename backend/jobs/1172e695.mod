MODULE ImageDraw
  ! Generated 2026-10-07 06:19 for ABB GoFa CRB 15000-5/0.95: 3 strokes
  ! Page 250 x 180 mm. Work object wPaper: Z points up, so pen-up is +Z and the tool uses orientation [0,1,0,0].
  PERS tooldata tPen:=[TRUE,[[0,0,120],[1,0,0,0]],[0.3,[0,0,60],[1,0,0,0],0,0,0]];
  PERS wobjdata wPaper:=[FALSE,TRUE,"",[[350,-90,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
  CONST robtarget pOrigin:=[[0,0,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
  CONST jointtarget jHome:=[[0,0,0,0,30,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
  CONST speeddata vTravel:=[250,200,5000,1000];

  PROC main()
    SingArea\Wrist;
    ConfL\Off;
    ConfJ\Off;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tPen;
    DrawPart1;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tPen;
  ENDPROC

  PROC DrawPart1()
    MoveL Offs(pOrigin,5.00,5.00,6.00),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,5.00,5.00,0.00),v60,z0,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,245.00,5.00,0.00),v40,z0,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,245.00,175.00,0.00),v40,z0,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,5.00,175.00,0.00),v40,z0,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,5.00,5.00,0.00),v40,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,5.00,5.00,6.00),v60,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,29.00,22.00,6.00),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,29.00,22.00,0.00),v60,z0,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,29.00,141.00,0.00),v40,z0,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,94.45,141.00,0.00),v40,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,94.45,141.00,6.00),v60,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,29.00,87.45,6.00),vTravel,z5,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,29.00,87.45,0.00),v60,z0,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,76.60,87.45,0.00),v40,fine,tPen\WObj:=wPaper;
    MoveL Offs(pOrigin,76.60,87.45,6.00),v60,z5,tPen\WObj:=wPaper;
  ENDPROC

ENDMODULE