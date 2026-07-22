//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : StructureEngine.mqh                                    |
//| Layer   : Brain / Trend / Engines                                |
//| Version : 3.0.0                                                  |
//| Purpose : Market Structure Analysis Engine                       |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_ENGINES_STRUCTUREENGINE_MQH
#define CORE_BRAIN_TREND_ENGINES_STRUCTUREENGINE_MQH

#include "../models/StructureResult.mqh"
#include "../models/SlopeResult.mqh"

//--------------------------------------------------
// Structure Engine
//--------------------------------------------------

class CStructureEngine
{
public:

   //--------------------------------------------------
   // Analyze
   //--------------------------------------------------

   CStructureResult Analyze(const CSlopeResult &slope)
   {
      CStructureResult result;

      //------------------------------------------------
      // Basic Structure Logic (Phase 1)
      //------------------------------------------------

      if(slope.Rising)
      {
         result.HigherHigh = true;
         result.HigherLow  = true;
         result.ValidStructure = true;
      }
      else
      if(slope.Falling)
      {
         result.LowerHigh = true;
         result.LowerLow  = true;
         result.ValidStructure = true;
      }

      return result;
   }
};

#endif