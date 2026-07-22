//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : CHOCHDetector.mqh                                      |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_DETECTORS_CHOCHDETECTOR_MQH
#define CORE_MARKET_DETECTORS_CHOCHDETECTOR_MQH

#include "../models/StructureState.mqh"

enum ENUM_CHOCH_DIRECTION
{
   CHOCH_NONE = 0,
   CHOCH_BULLISH,
   CHOCH_BEARISH
};

class CCHOCHState
{
public:

   ENUM_CHOCH_DIRECTION Direction;

   bool Valid;

   CCHOCHState()
   {
      Reset();
   }

   void Reset()
   {
      Direction = CHOCH_NONE;
      Valid = false;
   }
};

class CCHOCHDetector
{
public:

   bool Detect(
      const CStructureState &previousStructure,
      const CStructureState &currentStructure,
      CCHOCHState &result)
   {
      result.Reset();

      if(previousStructure.Trend < 0 &&
         currentStructure.Trend > 0)
      {
         result.Direction = CHOCH_BULLISH;
         result.Valid = true;
         return true;
      }

      if(previousStructure.Trend > 0 &&
         currentStructure.Trend < 0)
      {
         result.Direction = CHOCH_BEARISH;
         result.Valid = true;
         return true;
      }

      return false;
   }
};

#endif