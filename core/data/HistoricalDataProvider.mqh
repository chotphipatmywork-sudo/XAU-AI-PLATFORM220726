//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalDataProvider.mqh                             |
//| Layer   : Core / Data                                            |
//| Version : 1.0.0                                                  |
//| Purpose : Load aligned historical rates and ATR data             |
//+------------------------------------------------------------------+

#ifndef CORE_DATA_HISTORICALDATAPROVIDER_MQH
#define CORE_DATA_HISTORICALDATAPROVIDER_MQH

class CHistoricalDataProvider
  {
public:
   int LoadRates(const string symbol,const ENUM_TIMEFRAMES timeframe,const datetime from,const datetime to,MqlRates &rates[]) const
     {
      ArrayResize(rates,0);
      if(symbol=="" || from<=0 || to<=from)
         return(0);
      return(CopyRates(symbol,timeframe,from,to,rates));
     }

   int LoadAtr(const string symbol,const ENUM_TIMEFRAMES timeframe,const int period,const datetime from,const datetime to,double &atr_values[]) const
     {
      ArrayResize(atr_values,0);
      if(symbol=="" || period<=0 || from<=0 || to<=from)
         return(0);
      const int handle=iATR(symbol,timeframe,period);
      if(handle==INVALID_HANDLE)
         return(0);
      const int copied=CopyBuffer(handle,0,from,to,atr_values);
      IndicatorRelease(handle);
      return(copied);
     }
  };

#endif
