//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowStateStore.mqh                                   |
//| Layer   : Core / Execution / Shadow                              |
//| Version : 1.0.0                                                  |
//| Purpose : Persist and recover paper position state only          |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_SHADOW_SHADOWSTATESTORE_MQH
#define CORE_EXECUTION_SHADOW_SHADOWSTATESTORE_MQH

#include "models/ShadowTrade.mqh"

class CShadowStateStore
  {
private:
   string m_fileName;

public:
   CShadowStateStore()
     {
      m_fileName="XAU_AI_SHADOW_STATE.csv";
     }

   void SetFileName(const string fileName)
     {
      if(fileName!="")
         m_fileName=fileName;
     }

   bool Save(const CShadowTrade &trade)
     {
      const int handle=FileOpen(m_fileName,FILE_WRITE|FILE_CSV|FILE_ANSI,',');
      if(handle==INVALID_HANDLE)
         return(false);
      FileWrite(handle,
                "ticket","symbol","timeframe","order_type","volume",
                "entry_price","current_price","stop_loss","take_profit",
                "profit_points","open_time","close_time","active","close_reason");
      FileWrite(handle,
                (long)trade.Ticket,trade.Symbol,(int)trade.Timeframe,
                (int)trade.OrderType,trade.Volume,trade.EntryPrice,
                trade.CurrentPrice,trade.StopLoss,trade.TakeProfit,
                trade.ProfitPoints,(long)trade.OpenTime,(long)trade.CloseTime,
                trade.Active ? 1 : 0,trade.CloseReason);
      FileFlush(handle);
      FileClose(handle);
      return(true);
     }

   bool Load(CShadowTrade &trade)
     {
      trade.Reset();
      if(!FileIsExist(m_fileName))
         return(false);
      const int handle=FileOpen(m_fileName,
                                FILE_READ|FILE_CSV|FILE_ANSI|FILE_SHARE_READ,
                                ',');
      if(handle==INVALID_HANDLE)
         return(false);
      for(int index=0; index<14 && !FileIsEnding(handle); index++)
         FileReadString(handle);
      if(FileIsEnding(handle))
        {
         FileClose(handle);
         return(false);
        }
      trade.Ticket=(ulong)FileReadNumber(handle);
      trade.Symbol=FileReadString(handle);
      trade.Timeframe=(ENUM_TIMEFRAMES)(int)FileReadNumber(handle);
      trade.OrderType=(ENUM_ORDER_TYPE)(int)FileReadNumber(handle);
      trade.Volume=FileReadNumber(handle);
      trade.EntryPrice=FileReadNumber(handle);
      trade.CurrentPrice=FileReadNumber(handle);
      trade.StopLoss=FileReadNumber(handle);
      trade.TakeProfit=FileReadNumber(handle);
      trade.ProfitPoints=FileReadNumber(handle);
      trade.OpenTime=(datetime)(long)FileReadNumber(handle);
      trade.CloseTime=(datetime)(long)FileReadNumber(handle);
      trade.Active=((int)FileReadNumber(handle)==1);
      trade.CloseReason=FileReadString(handle);
      FileClose(handle);
      return(trade.Ticket>=900000001 && trade.Symbol!="" && trade.Volume>0.0);
     }
  };

#endif
