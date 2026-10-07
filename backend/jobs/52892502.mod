MODULE ImageDraw
  ! Generated 2026-10-07 12:48 for ABB GoFa CRB 15000-5/0.95: 3 strokes, 7 line/arc moves
  ! Page 250 x 180 mm. Work object Plywood: Z points DOWN, so pen-up is -Z and the tool uses orientation [6.123234E-17,0,0,1].
  ! Uses the tool 'tcp' and work object 'Plywood' that already exist on the controller.
  CONST jointtarget jHome:=[[0,0,0,0,30,0],[9E9,9E9,9E9,9E9,9E9,9E9]];
  CONST speeddata vTravel:=[250,200,5000,1000];

  PROC main()
    SingArea\Wrist;
    ConfL\On;
    ConfJ\On;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tcp;
    DrawPart1;
    MoveAbsJ jHome\NoEOffs,vTravel,fine,tcp;
  ENDPROC

  PROC DrawPart1()
    MoveL [[5.00,-5.00,-6.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],vTravel,z5,tcp\WObj:=Plywood;
    MoveL [[5.00,-5.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v60,z0,tcp\WObj:=Plywood;
    MoveL [[245.00,-5.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v40,z0,tcp\WObj:=Plywood;
    MoveL [[245.00,-175.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v40,z0,tcp\WObj:=Plywood;
    MoveL [[5.00,-175.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v40,z0,tcp\WObj:=Plywood;
    MoveL [[5.00,-5.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v40,fine,tcp\WObj:=Plywood;
    MoveL [[5.00,-5.00,-6.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v60,z5,tcp\WObj:=Plywood;
    MoveL [[29.00,-22.00,-6.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],vTravel,z5,tcp\WObj:=Plywood;
    MoveL [[29.00,-22.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v60,z0,tcp\WObj:=Plywood;
    MoveL [[29.00,-141.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v40,z0,tcp\WObj:=Plywood;
    MoveL [[94.45,-141.00,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v40,fine,tcp\WObj:=Plywood;
    MoveL [[94.45,-141.00,-6.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v60,z5,tcp\WObj:=Plywood;
    MoveL [[29.00,-87.45,-6.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],vTravel,z5,tcp\WObj:=Plywood;
    MoveL [[29.00,-87.45,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v60,z0,tcp\WObj:=Plywood;
    MoveL [[76.60,-87.45,0.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v40,fine,tcp\WObj:=Plywood;
    MoveL [[76.60,-87.45,-6.00],[6.123234E-17,0,0,1],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],v60,z5,tcp\WObj:=Plywood;
  ENDPROC

ENDMODULE