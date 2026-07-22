//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalPriceActionContextExporter.mqh               |
//| Layer   : Core / AI / Learning / Research                        |
//| Version : 1.0.0                                                  |
//| Purpose : Export bounded past-only completed-bar price context   |
//+------------------------------------------------------------------+

#ifndef CORE_AI_HISTORICALPRICEACTIONCONTEXTEXPORTER_MQH
#define CORE_AI_HISTORICALPRICEACTIONCONTEXTEXPORTER_MQH

#include "storage/DatasetReader.mqh"

class CHistoricalPriceActionContextExporter
  {
private:
   bool IsPositivePrice(const double value) const
     {
      return(value>0.0);
     }

   bool LoadPriorRange(const string symbol,const ENUM_TIMEFRAMES timeframe,
                       const int shift,double &range_high,
                       double &range_low) const
     {
      range_high=0.0;
      range_low=0.0;
      for(int offset=1; offset<=16; offset++)
        {
         const double high=iHigh(symbol,timeframe,shift+offset);
         const double low=iLow(symbol,timeframe,shift+offset);
         if(!IsPositivePrice(high) || !IsPositivePrice(low) || high<low)
            return(false);
         if(offset==1 || high>range_high)
            range_high=high;
         if(offset==1 || low<range_low)
            range_low=low;
        }
      return(range_high>range_low);
     }

   bool WriteNeutral(const int handle,const CDatasetRecord &record) const
     {
      return(FileWrite(handle,record.Id(),record.Timestamp(),
                       50.0,50.0,50.0,50.0,50.0,50.0,50.0,50.0,
                       0.0)>0);
     }

public:
   double EncodeSignedAtr(const double value,const double atr) const
     {
      if(atr<=0.0)
         return(50.0);
      return(MathMax(0.0,MathMin(100.0,50.0+25.0*value/atr)));
     }

   double EncodePositiveAtr(const double value,const double atr) const
     {
      if(value<0.0 || atr<=0.0)
         return(50.0);
      return(MathMax(0.0,MathMin(100.0,50.0*value/atr)));
     }

   double RangePosition(const double value,const double low,
                        const double high) const
     {
      if(high<=low)
         return(50.0);
      return(MathMax(0.0,MathMin(100.0,
             100.0*(value-low)/(high-low))));
     }

   datetime ObservationTime(const datetime bar_open,
                            const ENUM_TIMEFRAMES timeframe) const
     {
      const int seconds=PeriodSeconds(timeframe);
      if(bar_open<=0 || seconds<=0)
         return(0);
      return(bar_open+seconds);
     }

   bool IsBarClosed(const datetime bar_open,const datetime observation_time,
                    const ENUM_TIMEFRAMES timeframe) const
     {
      return(bar_open>0 && observation_time>0 &&
             bar_open+PeriodSeconds(timeframe)<=observation_time);
     }

   int Export(const string dataset_file,const string output_file,
              const int progress_interval=100)
     {
      if(dataset_file=="" || output_file=="" || progress_interval<=0)
         return(-1);
      CDatasetReader reader;
      if(!reader.Initialize(dataset_file))
         return(-1);
      if(FileIsExist(output_file) && !FileDelete(output_file))
        {
         reader.Shutdown();
         return(-1);
        }
      const int handle=FileOpen(output_file,FILE_CSV|FILE_WRITE|FILE_ANSI,',');
      if(handle==INVALID_HANDLE)
        {
         reader.Shutdown();
         return(-1);
        }
      FileWrite(handle,"id","timestamp","price_return_1_atr",
                "price_return_4_atr","price_return_16_atr",
                "candle_body_atr","candle_range_atr",
                "candle_close_location","prior_range_width_atr",
                "prior_range_position","price_action_valid");

      int atr_handle=INVALID_HANDLE;
      string atr_symbol="";
      int written=0;
      CDatasetRecord record;
      while(reader.Read(record))
        {
         if(atr_handle==INVALID_HANDLE)
           {
            atr_symbol=record.Symbol();
            atr_handle=iATR(atr_symbol,PERIOD_M15,14);
            if(atr_handle==INVALID_HANDLE)
              {
               FileClose(handle);
               reader.Shutdown();
               return(-1);
              }
           }
         if(record.Symbol()!=atr_symbol)
           {
            IndicatorRelease(atr_handle);
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         const int shift=iBarShift(record.Symbol(),PERIOD_M15,
                                   record.Timestamp(),true);
         const datetime observation=ObservationTime(record.Timestamp(),PERIOD_M15);
         if(shift<0 || !IsBarClosed(record.Timestamp(),observation,PERIOD_M15))
           {
            IndicatorRelease(atr_handle);
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }

         double atr_buffer[];
         const bool atr_valid=(CopyBuffer(atr_handle,0,shift,1,atr_buffer)==1 &&
                               atr_buffer[0]>0.0);
         const double open=iOpen(record.Symbol(),PERIOD_M15,shift);
         const double high=iHigh(record.Symbol(),PERIOD_M15,shift);
         const double low=iLow(record.Symbol(),PERIOD_M15,shift);
         const double close=iClose(record.Symbol(),PERIOD_M15,shift);
         const double close_1=iClose(record.Symbol(),PERIOD_M15,shift+1);
         const double close_4=iClose(record.Symbol(),PERIOD_M15,shift+4);
         const double close_16=iClose(record.Symbol(),PERIOD_M15,shift+16);
         double prior_high=0.0;
         double prior_low=0.0;
         const bool range_valid=LoadPriorRange(record.Symbol(),PERIOD_M15,
                                               shift,prior_high,prior_low);
         const bool prices_valid=(IsPositivePrice(open) &&
                                  IsPositivePrice(high) &&
                                  IsPositivePrice(low) &&
                                  IsPositivePrice(close) &&
                                  IsPositivePrice(close_1) &&
                                  IsPositivePrice(close_4) &&
                                  IsPositivePrice(close_16) &&
                                  high>low);

         bool row_written=false;
         if(!atr_valid || !prices_valid || !range_valid)
            row_written=WriteNeutral(handle,record);
         else
           {
            const double atr=atr_buffer[0];
            row_written=(FileWrite(
               handle,record.Id(),record.Timestamp(),
               EncodeSignedAtr(close-close_1,atr),
               EncodeSignedAtr(close-close_4,atr),
               EncodeSignedAtr(close-close_16,atr),
               EncodeSignedAtr(close-open,atr),
               EncodePositiveAtr(high-low,atr),
               RangePosition(close,low,high),
               EncodePositiveAtr(prior_high-prior_low,atr),
               RangePosition(close,prior_low,prior_high),
               100.0)>0);
           }
         if(!row_written)
           {
            IndicatorRelease(atr_handle);
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         written++;
         if(written%progress_interval==0)
           {
            FileFlush(handle);
            Print("Historical price action context export progress: ",
                  written," records");
           }
        }
      if(atr_handle!=INVALID_HANDLE)
         IndicatorRelease(atr_handle);
      FileFlush(handle);
      FileClose(handle);
      reader.Shutdown();
      return(written);
     }
  };

#endif
