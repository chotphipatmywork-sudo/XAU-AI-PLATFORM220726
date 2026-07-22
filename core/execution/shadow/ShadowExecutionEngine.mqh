//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowExecutionEngine.mqh                              |
//| Layer   : Core / Execution / Shadow                             |
//| Version : 1.3.0                                                  |
//| Purpose : Simulate approved execution without broker mutation    |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_SHADOW_SHADOWEXECUTIONENGINE_MQH
#define CORE_EXECUTION_SHADOW_SHADOWEXECUTIONENGINE_MQH

#include "../models/ExecutionContext.mqh"
#include "../models/ExecutionResult.mqh"
#include "../../risk/models/RiskResult.mqh"
#include "ShadowExecutionConfig.mqh"
#include "ShadowAuditLogger.mqh"
#include "ShadowStateStore.mqh"
#include "models/ShadowTrade.mqh"
#include "../models/ExecutionPricePlan.mqh"

class CShadowExecutionEngine
  {
private:
   CShadowExecutionConfig m_config;
   CShadowAuditLogger     m_logger;
   CShadowStateStore      m_stateStore;
   CShadowTrade           m_trade;
   ulong                  m_nextTicket;
   bool                   m_emergencyStop;
   double                 m_dailyProfitPoints;
   double                 m_cumulativeProfitPoints;
   double                 m_peakProfitPoints;
   double                 m_maximumDrawdownPoints;
   datetime               m_profitDay;
   ulong                  m_closedTrades;
   ulong                  m_winningTrades;
   ulong                  m_losingTrades;
   ulong                  m_breakevenTrades;
   datetime               m_lastStateCheckpoint;

   void Reject(CExecutionResult &result,
               const string message,
               const double riskScore,
               const double confidence)
     {
      result.Reset();
      result.Status=EXECUTION_REJECTED;
      result.Message=message;
      m_logger.Write("REJECTED",message,m_trade,riskScore,confidence);
     }

public:
   CShadowExecutionEngine()
     {
      m_nextTicket=900000001;
      m_emergencyStop=false;
      m_dailyProfitPoints=0.0;
      m_cumulativeProfitPoints=0.0;
      m_peakProfitPoints=0.0;
      m_maximumDrawdownPoints=0.0;
      m_profitDay=0;
      m_closedTrades=0;
      m_winningTrades=0;
      m_losingTrades=0;
      m_breakevenTrades=0;
      m_lastStateCheckpoint=0;
     }

   void RefreshDay(const datetime currentTime)
     {
      MqlDateTime current;
      MqlDateTime tracked;
      TimeToStruct(currentTime,current);
      TimeToStruct(m_profitDay,tracked);
      if(m_profitDay==0 ||
         current.year!=tracked.year ||
         current.mon!=tracked.mon ||
         current.day!=tracked.day)
        {
         m_dailyProfitPoints=0.0;
         m_profitDay=currentTime;
        }
     }

   bool Initialize(const CShadowExecutionConfig &config)
     {
      if(!config.Valid())
         return(false);
      m_config=config;
      m_logger.SetFileName(config.AuditFile);
      m_stateStore.SetFileName(config.StateFile);
      const bool recovered=m_stateStore.Load(m_trade);
      if(!recovered)
         m_trade.Reset();
      else
        {
         if(m_trade.Ticket>=m_nextTicket)
            m_nextTicket=m_trade.Ticket+1;
         if(m_trade.Active)
            m_logger.Write("RECOVERED",
                           "Recovered active paper position after restart.",
                           m_trade,0.0,0.0);
        }
      m_emergencyStop=false;
      m_dailyProfitPoints=0.0;
      m_cumulativeProfitPoints=0.0;
      m_peakProfitPoints=0.0;
      m_maximumDrawdownPoints=0.0;
      m_profitDay=TimeCurrent();
      m_closedTrades=0;
      m_winningTrades=0;
      m_losingTrades=0;
      m_breakevenTrades=0;
      m_lastStateCheckpoint=TimeCurrent();
      return(true);
     }

   void SetEmergencyStop(const bool enabled)
     {
      m_emergencyStop=enabled;
      if(enabled)
        {
         m_logger.Write("EMERGENCY_STOP","Emergency stop enabled.",m_trade,0.0,0.0);
         if(m_trade.Active)
            Close("EMERGENCY_STOP",TimeCurrent());
        }
     }

   bool EmergencyStopEnabled() const
     {
      return(m_emergencyStop);
     }

   CExecutionResult Execute(const CExecutionContext &context,
                            const CRiskResult &risk)
     {
      CExecutionResult result;
      RefreshDay(context.CurrentTime>0 ? context.CurrentTime : TimeCurrent());

      if(m_emergencyStop || risk.EmergencyStop)
        {
         Reject(result,"Shadow execution blocked by emergency stop.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }
      if(!risk.Valid || !risk.AllowTrade || risk.Level==RISK_BLOCK)
        {
         Reject(result,"Shadow execution requires explicit Risk approval.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }
      if(!context.Decision.Valid)
        {
         Reject(result,"Shadow execution received an invalid Decision.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }
      if(context.Decision.Decision!=DECISION_BUY &&
         context.Decision.Decision!=DECISION_SELL)
        {
         Reject(result,"Shadow execution accepts BUY or SELL only.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }
      if(context.Symbol=="" || context.Point<=0.0 ||
         context.Ask<=0.0 || context.Bid<=0.0)
        {
         Reject(result,"Shadow execution market context is invalid.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }
      if(m_config.OnePositionOnly && m_trade.Active)
        {
         Reject(result,"Shadow paper position already exists.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }

      m_trade.Reset();
      m_trade.Ticket=m_nextTicket++;
      m_trade.Symbol=context.Symbol;
      m_trade.Timeframe=context.Timeframe;
      m_trade.Volume=m_config.DefaultVolume;
      m_trade.OpenTime=context.CurrentTime>0 ? context.CurrentTime : TimeCurrent();
      m_trade.Active=true;

      if(context.Decision.Decision==DECISION_BUY)
        {
         m_trade.OrderType=ORDER_TYPE_BUY;
         m_trade.EntryPrice=context.Ask+
                            m_config.SimulatedSlippagePoints*context.Point;
         m_trade.CurrentPrice=context.Bid;
         m_trade.StopLoss=m_trade.EntryPrice-m_config.StopLossPoints*context.Point;
         m_trade.TakeProfit=m_trade.EntryPrice+m_config.TakeProfitPoints*context.Point;
        }
      else
        {
         m_trade.OrderType=ORDER_TYPE_SELL;
         m_trade.EntryPrice=context.Bid-
                            m_config.SimulatedSlippagePoints*context.Point;
         m_trade.CurrentPrice=context.Ask;
         m_trade.StopLoss=m_trade.EntryPrice+m_config.StopLossPoints*context.Point;
         m_trade.TakeProfit=m_trade.EntryPrice-m_config.TakeProfitPoints*context.Point;
        }

      m_stateStore.Save(m_trade);
      m_lastStateCheckpoint=m_trade.OpenTime;
      result.Success=true;
      result.Status=EXECUTION_SUCCESS;
      result.OrderType=m_trade.OrderType;
      result.LotSize=m_trade.Volume;
      result.EntryPrice=m_trade.EntryPrice;
      result.StopLoss=m_trade.StopLoss;
      result.TakeProfit=m_trade.TakeProfit;
      result.MagicNumber=88001;
      result.Ticket=m_trade.Ticket;
      result.Comment="XAU AI SHADOW";
      result.Message="Shadow paper position opened; no broker order sent.";
      m_logger.Write("OPENED",result.Message,m_trade,
                     risk.Score,context.Decision.Confidence);
      return(result);
     }

   CExecutionResult Execute(const CExecutionContext &context,
                            const CRiskResult &risk,
                            const CExecutionPricePlan &pricePlan)
     {
      CExecutionResult result;

      // Risk and emergency protection remain the first permission boundary.
      if(m_emergencyStop || risk.EmergencyStop ||
         !risk.Valid || !risk.AllowTrade || risk.Level==RISK_BLOCK)
         return(Execute(context,risk));

      if(!context.Decision.Valid ||
         (context.Decision.Decision!=DECISION_BUY &&
          context.Decision.Decision!=DECISION_SELL) ||
         context.Symbol=="" || context.Point<=0.0 ||
         context.Ask<=0.0 || context.Bid<=0.0 ||
         (m_config.OnePositionOnly && m_trade.Active))
         return(Execute(context,risk));

      if(!pricePlan.ContractValid())
        {
         Reject(result,"Shadow structural execution requires a valid price plan.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }
      if(pricePlan.Direction!=context.Decision.Decision)
        {
         Reject(result,"Shadow structural price-plan direction mismatch.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }

      const double simulatedEntry=
         (context.Decision.Decision==DECISION_BUY ?
          context.Ask+m_config.SimulatedSlippagePoints*context.Point :
          context.Bid-m_config.SimulatedSlippagePoints*context.Point);
      const bool buyGeometry=
         (context.Decision.Decision==DECISION_BUY &&
          pricePlan.StopLossPrice<simulatedEntry &&
          pricePlan.TakeProfitPrice>simulatedEntry);
      const bool sellGeometry=
         (context.Decision.Decision==DECISION_SELL &&
          pricePlan.StopLossPrice>simulatedEntry &&
          pricePlan.TakeProfitPrice<simulatedEntry);
      if(!buyGeometry && !sellGeometry)
        {
         Reject(result,"Shadow structural price-plan geometry is invalid at simulated entry.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }

      const double riskPoints=
         MathAbs(simulatedEntry-pricePlan.StopLossPrice)/context.Point+
         pricePlan.EstimatedCostPoints;
      const double rewardPoints=
         MathAbs(pricePlan.TakeProfitPrice-simulatedEntry)/context.Point-
         pricePlan.EstimatedCostPoints;
      const double actualRiskReward=
         (riskPoints>0.0 ? rewardPoints/riskPoints : 0.0);
      if(!MathIsValidNumber(riskPoints) ||
         !MathIsValidNumber(rewardPoints) ||
         !MathIsValidNumber(actualRiskReward) ||
         riskPoints<=0.0 || rewardPoints<=0.0 ||
         actualRiskReward+0.000000001<pricePlan.MinimumRiskReward)
        {
         Reject(result,"Shadow structural price plan fell below minimum RR at simulated entry.",
                risk.Score,context.Decision.Confidence);
         return(result);
        }

      const double fixedStopLossPoints=m_config.StopLossPoints;
      const double fixedTakeProfitPoints=m_config.TakeProfitPoints;
      m_config.StopLossPoints=
         MathAbs(simulatedEntry-pricePlan.StopLossPrice)/context.Point;
      m_config.TakeProfitPoints=
         MathAbs(pricePlan.TakeProfitPrice-simulatedEntry)/context.Point;
      result=Execute(context,risk);
      m_config.StopLossPoints=fixedStopLossPoints;
      m_config.TakeProfitPoints=fixedTakeProfitPoints;

      if(result.Success)
         result.Message=
            "Shadow structural paper position opened; supplied Stop/Target preserved; no broker order sent.";
      return(result);
     }

   bool Update(const double bid,
               const double ask,
               const double point,
               const datetime currentTime)
     {
      if(!m_trade.Active || bid<=0.0 || ask<=0.0 || point<=0.0)
         return(false);
      RefreshDay(currentTime>0 ? currentTime : TimeCurrent());

      if(currentTime>0 &&
         m_trade.OpenTime>0 &&
         currentTime-m_trade.OpenTime >=
         (long)m_config.MaximumHoldingBars*PeriodSeconds(m_trade.Timeframe))
        {
         if(m_trade.OrderType==ORDER_TYPE_BUY)
           {
            m_trade.CurrentPrice=bid;
            m_trade.ProfitPoints=(bid-m_trade.EntryPrice)/point;
           }
         else
           {
            m_trade.CurrentPrice=ask;
            m_trade.ProfitPoints=(m_trade.EntryPrice-ask)/point;
           }
         return(Close("MAX_HOLDING_TIME",currentTime));
        }

      if(m_trade.OrderType==ORDER_TYPE_BUY)
        {
         m_trade.CurrentPrice=bid;
         m_trade.ProfitPoints=(bid-m_trade.EntryPrice)/point;
         if(bid<=m_trade.StopLoss)
            return(Close("STOP_LOSS",currentTime));
         if(bid>=m_trade.TakeProfit)
            return(Close("TAKE_PROFIT",currentTime));
        }
      else
        {
         m_trade.CurrentPrice=ask;
         m_trade.ProfitPoints=(m_trade.EntryPrice-ask)/point;
         if(ask>=m_trade.StopLoss)
            return(Close("STOP_LOSS",currentTime));
         if(ask<=m_trade.TakeProfit)
            return(Close("TAKE_PROFIT",currentTime));
        }
      const datetime checkpointTime=(currentTime>0 ? currentTime : TimeCurrent());
      if(m_lastStateCheckpoint<=0 ||
         checkpointTime-m_lastStateCheckpoint>=m_config.StateCheckpointSeconds)
        {
         m_stateStore.Save(m_trade);
         m_lastStateCheckpoint=checkpointTime;
        }
      return(true);
     }

   bool Close(const string reason,
              const datetime currentTime)
     {
      if(!m_trade.Active)
         return(false);
      m_trade.Active=false;
      m_trade.CloseReason=reason;
      m_trade.CloseTime=currentTime>0 ? currentTime : TimeCurrent();
      RefreshDay(m_trade.CloseTime);
      m_dailyProfitPoints+=m_trade.ProfitPoints;
      m_cumulativeProfitPoints+=m_trade.ProfitPoints;
      if(m_cumulativeProfitPoints>m_peakProfitPoints)
         m_peakProfitPoints=m_cumulativeProfitPoints;
      const double currentDrawdown=MathMax(
         0.0,m_peakProfitPoints-m_cumulativeProfitPoints);
      if(currentDrawdown>m_maximumDrawdownPoints)
         m_maximumDrawdownPoints=currentDrawdown;
      m_closedTrades++;
      if(m_trade.ProfitPoints>0.0)
         m_winningTrades++;
      else if(m_trade.ProfitPoints<0.0)
         m_losingTrades++;
      else
         m_breakevenTrades++;
      m_logger.Write("CLOSED",reason,m_trade,0.0,0.0);
      m_stateStore.Save(m_trade);
      m_lastStateCheckpoint=m_trade.CloseTime;
      return(true);
     }

   void Shutdown()
     {
      if(m_trade.Active)
         Close("EA_SHUTDOWN",TimeCurrent());
     }

   bool HasActivePosition() const
     {
      return(m_trade.Active);
     }

   CShadowTrade Snapshot() const
     {
      return(m_trade);
     }

   double DailyProfitPoints() const
     {
      return(m_dailyProfitPoints);
     }

   double CumulativeProfitPoints() const
     {
      return(m_cumulativeProfitPoints);
     }

   double DrawdownPoints() const
     {
      return(MathMax(0.0,m_peakProfitPoints-m_cumulativeProfitPoints));
     }

   double MaximumDrawdownPoints() const
     {
      return(m_maximumDrawdownPoints);
     }

   ulong ClosedTradeCount() const
     {
      return(m_closedTrades);
     }

   ulong WinningTradeCount() const
     {
      return(m_winningTrades);
     }

   ulong LosingTradeCount() const
     {
      return(m_losingTrades);
     }

   ulong BreakevenTradeCount() const
     {
      return(m_breakevenTrades);
     }
  };

#endif
