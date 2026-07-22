//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowExecutionManager.mqh                             |
//| Layer   : Core / Execution / Shadow                              |
//| Version : 1.2.0                                                  |
//| Purpose : Shadow adapter facade for canonical Runtime            |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_SHADOW_SHADOWEXECUTIONMANAGER_MQH
#define CORE_EXECUTION_SHADOW_SHADOWEXECUTIONMANAGER_MQH

#include "../builder/ExecutionContextBuilder.mqh"
#include "../../risk/models/RiskResult.mqh"
#include "ShadowExecutionEngine.mqh"

class CShadowExecutionManager
  {
private:
   CExecutionContextBuilder m_builder;
   CShadowExecutionEngine   m_engine;
   bool                     m_initialized;

public:
   CShadowExecutionManager()
     {
      m_initialized=false;
     }

   bool Initialize(const CShadowExecutionConfig &config)
     {
      m_initialized=m_engine.Initialize(config);
      return(m_initialized);
     }

   CExecutionResult Execute(const CDecisionResult &decision,
                            const CRiskResult &risk,
                            const string symbol,
                            const ENUM_TIMEFRAMES timeframe)
     {
      CExecutionResult result;
      if(!m_initialized)
        {
         result.Status=EXECUTION_REJECTED;
         result.Message="ShadowExecutionManager not initialized.";
         return(result);
        }

      CExecutionContext context;
      if(!m_builder.Build(decision,symbol,timeframe,context))
        {
         result.Status=EXECUTION_REJECTED;
         result.Message="Unable to build Shadow execution context.";
         return(result);
        }
      return(m_engine.Execute(context,risk));
     }

   CExecutionResult Execute(const CDecisionResult &decision,
                            const CRiskResult &risk,
                            const string symbol,
                            const ENUM_TIMEFRAMES timeframe,
                            const CExecutionPricePlan &pricePlan)
     {
      CExecutionResult result;
      if(!m_initialized)
        {
         result.Status=EXECUTION_REJECTED;
         result.Message="ShadowExecutionManager not initialized.";
         return(result);
        }

      CExecutionContext context;
      if(!m_builder.Build(decision,symbol,timeframe,context))
        {
         result.Status=EXECUTION_REJECTED;
         result.Message="Unable to build Shadow execution context.";
         return(result);
        }
      return(m_engine.Execute(context,risk,pricePlan));
     }

   bool Update(const string symbol)
     {
      if(!m_initialized || !m_engine.HasActivePosition())
         return(false);
      MqlTick tick;
      if(!SymbolInfoTick(symbol,tick))
         return(false);
      const double point=SymbolInfoDouble(symbol,SYMBOL_POINT);
      return(m_engine.Update(tick.bid,tick.ask,point,TimeCurrent()));
     }

   void SetEmergencyStop(const bool enabled)
     {
      m_engine.SetEmergencyStop(enabled);
     }

   bool HasActivePosition() const
     {
      return(m_engine.HasActivePosition());
     }

   CShadowTrade Snapshot() const
     {
      return(m_engine.Snapshot());
     }

   double DailyProfitPoints() const
     {
      return(m_engine.DailyProfitPoints());
     }

   double CumulativeProfitPoints() const
     {
      return(m_engine.CumulativeProfitPoints());
     }

   double DrawdownPoints() const
     {
      return(m_engine.DrawdownPoints());
     }

   double MaximumDrawdownPoints() const
     {
      return(m_engine.MaximumDrawdownPoints());
     }

   ulong ClosedTradeCount() const
     {
      return(m_engine.ClosedTradeCount());
     }

   ulong WinningTradeCount() const
     {
      return(m_engine.WinningTradeCount());
     }

   ulong LosingTradeCount() const
     {
      return(m_engine.LosingTradeCount());
     }

   ulong BreakevenTradeCount() const
     {
      return(m_engine.BreakevenTradeCount());
     }

   bool MarketStale(const string symbol,const int maximumAgeSeconds) const
     {
      MqlTick tick;
      if(maximumAgeSeconds<=0 || !SymbolInfoTick(symbol,tick) || tick.time<=0)
         return(true);
      return((TimeCurrent()-tick.time)>maximumAgeSeconds);
     }

   void Shutdown()
     {
      m_engine.Shutdown();
      m_initialized=false;
     }
  };

#endif
