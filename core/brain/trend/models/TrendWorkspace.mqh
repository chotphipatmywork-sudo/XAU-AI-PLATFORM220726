//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TrendWorkspace.mqh                                     |
//| Layer   : Brain / Trend / Models                                 |
//| Version : 2.2.0                                                  |
//| Purpose : Working Memory for Trend Package                       |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_TRENDWORKSPACE_MQH
#define CORE_BRAIN_TREND_MODELS_TRENDWORKSPACE_MQH

#include "TrendContext.mqh"

#include "../../../indicators/models/EMAResult.mqh"
#include "SlopeResult.mqh"
#include "StructureResult.mqh"
#include "BOSResult.mqh"
#include "CHOCHResult.mqh"

//--------------------------------------------------
// Trend Workspace
//--------------------------------------------------

class CTrendWorkspace
{
public:

   //--------------------------------------------------
   // Input
   //--------------------------------------------------

   CTrendContext Context;

   //--------------------------------------------------
   // Engine Results
   //--------------------------------------------------

   CEMAResult EMA;

   CSlopeResult Slope;

   double ATR;

   double FastEMALookback;

   CStructureResult Structure;

   CBOSResult BOS;

   CCHOCHResult CHOCH;

   //--------------------------------------------------
   // Constructor
   //--------------------------------------------------

   CTrendWorkspace()
   {
   }

   //--------------------------------------------------
   // Reset
   //--------------------------------------------------

   void Reset()
   {
      Context   = CTrendContext();

      EMA       = CEMAResult();

      Slope     = CSlopeResult();

      ATR       = 0.0;

      FastEMALookback = 0.0;

      Structure = CStructureResult();

      BOS       = CBOSResult();

      CHOCH     = CCHOCHResult();
   }
};

#endif
