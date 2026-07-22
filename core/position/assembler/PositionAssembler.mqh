//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionAssembler.mqh                                  |
//| Layer   : Core /Position /Assembler                              |
//| Version : 1.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_ASSEMBLER_POSITIONASSEMBLER_MQH
#define CORE_POSITION_ASSEMBLER_POSITIONASSEMBLER_MQH

#include "../models/PositionResult.mqh"

//--------------------------------------------------

class CPositionAssembler
{
public:

   CPositionResult Assemble(const CPositionResult &result)
   {
      return result;
   }
};

#endif