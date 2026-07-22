//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LiquidityAnalyzer.mqh                                  |
//| Layer   : Brain                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_LIQUIDITYANALYZER_MQH
#define CORE_BRAIN_LIQUIDITYANALYZER_MQH

#include "liquidity/models/LiquidityContext.mqh"
#include "liquidity/models/LiquidityResult.mqh"

#include "liquidity/config/LiquidityConfig.mqh"
#include "liquidity/engines/LiquidityEngine.mqh"

//--------------------------------------------------

class CLiquidityAnalyzer
{
private:

   CLiquidityConfig m_config;

   CLiquidityEngine m_engine;

public:

   void SetConfig(const CLiquidityConfig &config)
   {
      m_config = config;
      m_engine.SetConfig(config);
   }

   //--------------------------------------------------

   CLiquidityResult Analyze(
      const CLiquidityContext &context)
   {
      return m_engine.Analyze(context);
   }
};

#endif