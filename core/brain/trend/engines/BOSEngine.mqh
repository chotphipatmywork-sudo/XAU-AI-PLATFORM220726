//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BOSEngine.mqh                                          |
//| Layer   : Brain / Trend / Engines                                |
//| Version : 3.0.0                                                  |
//| Purpose : Break Of Structure Analysis Engine                     |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_ENGINES_BOSENGINE_MQH
#define CORE_BRAIN_TREND_ENGINES_BOSENGINE_MQH

#include "../models/BOSResult.mqh"
#include "../models/StructureResult.mqh"

//--------------------------------------------------

class CBOSEngine
{
public:

   CBOSResult Analyze(const CStructureResult &structure)
   {
      CBOSResult result;

      if(!structure.ValidStructure)
         return result;

      result.ValidBreak = true;

      if(structure.HigherHigh)
         result.BullishBreak = true;

      if(structure.LowerLow)
         result.BearishBreak = true;

      return result;
   }
};

#endif