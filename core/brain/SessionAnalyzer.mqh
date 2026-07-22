//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SessionAnalyzer.mqh                                    |
//| Layer   : Brain                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SESSIONANALYZER_MQH
#define CORE_BRAIN_SESSIONANALYZER_MQH

#include "session/config/SessionConfig.mqh"

#include "session/models/SessionContext.mqh"
#include "session/models/SessionResult.mqh"

#include "session/engines/SessionEngine.mqh"

//--------------------------------------------------

class CSessionAnalyzer
{
private:

   CSessionConfig m_config;

   CSessionEngine m_engine;

public:

   void SetConfig(const CSessionConfig &config)
   {
      m_config = config;
      m_engine.SetConfig(config);
   }

   //--------------------------------------------------

   CSessionResult Analyze(
      const CSessionContext &context)
   {
      return m_engine.Analyze(context);
   }
};

#endif