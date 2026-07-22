//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowAuditLogger.mqh                                  |
//| Layer   : Core / Execution / Shadow                             |
//| Version : 1.0.0                                                  |
//| Purpose : Append-only paper-execution CSV audit writer           |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_SHADOW_SHADOWAUDITLOGGER_MQH
#define CORE_EXECUTION_SHADOW_SHADOWAUDITLOGGER_MQH

#include "models/ShadowTrade.mqh"

class CShadowAuditLogger
  {
private:
   string m_fileName;

public:
   CShadowAuditLogger()
     {
      m_fileName="XAU_AI_SHADOW_AUDIT.csv";
     }

   void SetFileName(const string fileName)
     {
      if(fileName!="")
         m_fileName=fileName;
     }

   bool Write(const string eventName,
              const string message,
              const CShadowTrade &trade,
              const double riskScore,
              const double confidence)
     {
      const int handle=FileOpen(m_fileName,
                                FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ,
                                ',');
      if(handle==INVALID_HANDLE)
         return(false);

      if(FileSize(handle)==0)
         FileWrite(handle,
                   "timestamp","event","message","ticket","symbol","order_type",
                   "volume","entry_price","current_price","stop_loss","take_profit",
                   "profit_points","active","risk_score","confidence");

      FileSeek(handle,0,SEEK_END);
      FileWrite(handle,
                TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),
                eventName,
                message,
                (long)trade.Ticket,
                trade.Symbol,
                EnumToString(trade.OrderType),
                trade.Volume,
                trade.EntryPrice,
                trade.CurrentPrice,
                trade.StopLoss,
                trade.TakeProfit,
                trade.ProfitPoints,
                trade.Active ? "true" : "false",
                riskScore,
                confidence);
      FileFlush(handle);
      FileClose(handle);
      return(true);
     }
  };

#endif
