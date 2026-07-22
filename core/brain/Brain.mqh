//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Brain.mqh                                              |
//| Layer   : Brain                                                  |
//| Version : 3.2.0                                                  |
//| Purpose : Brain Core                                             |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_BRAIN_MQH
#define CORE_BRAIN_BRAIN_MQH

#include "SignalEngine.mqh"
#include "trend/providers/ClosedBarSwingStructureProvider.mqh"

#include "../engine/models/BrainPipelineResult.mqh"

//--------------------------------------------------

class CBrain
{
private:

   CSignalEngine m_signalEngine;

   CClosedBarSwingStructureProvider m_swingStructureProvider;

public:

   //--------------------------------------------------

   bool Initialize()
   {
      return true;
   }

   //--------------------------------------------------

   CBrainPipelineResult Think(
      const string symbol,
      ENUM_TIMEFRAMES timeframe,
      const int shift=0)
   {
      return
         m_signalEngine.Generate(
            symbol,
            timeframe,
            shift);
   }

   bool ConfirmedSwingStructure(
      const string symbol,
      const ENUM_TIMEFRAMES timeframe,
      const int shift,
      const datetime expectedBarOpen,
      const datetime observationTime,
      CConfirmedSwingStructureResult &result) const
   {
      return(m_swingStructureProvider.Analyze(
         symbol,timeframe,shift,expectedBarOpen,observationTime,result));
   }

   //--------------------------------------------------

   void Shutdown()
   {
   }
};

#endif
