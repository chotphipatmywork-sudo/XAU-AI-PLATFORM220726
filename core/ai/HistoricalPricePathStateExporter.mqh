//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalPricePathStateExporter.mqh                   |
//| Layer   : Core / AI / Learning / Research                        |
//| Version : 1.0.0                                                  |
//| Purpose : Export completed 16-bar price-path state by Dataset row|
//+------------------------------------------------------------------+

#ifndef CORE_AI_HISTORICALPRICEPATHSTATEEXPORTER_MQH
#define CORE_AI_HISTORICALPRICEPATHSTATEEXPORTER_MQH

#include "storage/DatasetReader.mqh"
#include "../brain/trend/engines/PricePathStateEngine.mqh"

class CHistoricalPricePathStateExporter
  {
private:
   CPricePathStateEngine m_engine;

   bool LoadPath(const string symbol,const ENUM_TIMEFRAMES timeframe,
                 const int shift,double &closes[],double &highs[],
                 double &lows[]) const
     {
      ArrayResize(closes,17);
      ArrayResize(highs,16);
      ArrayResize(lows,16);
      for(int index=0; index<17; index++)
        {
         closes[index]=iClose(symbol,timeframe,shift+index);
         if(closes[index]<=0.0)
            return(false);
         if(index<16)
           {
            highs[index]=iHigh(symbol,timeframe,shift+index);
            lows[index]=iLow(symbol,timeframe,shift+index);
            if(highs[index]<=0.0 || lows[index]<=0.0 ||
               highs[index]<lows[index])
               return(false);
           }
        }
      return(true);
     }

   bool WriteNeutral(const int handle,const CDatasetRecord &record) const
     {
      return(FileWrite(handle,record.Id(),record.Timestamp(),
                       50.0,50.0,50.0,50.0,50.0,50.0,50.0,0.0)>0);
     }

public:
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
      FileWrite(handle,"id","timestamp","path_directional_efficiency",
                "up_close_ratio","directional_run_balance",
                "return_sign_persistence","path_travel_atr",
                "range_efficiency","range_expansion","price_path_valid");

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
         double closes[];
         double highs[];
         double lows[];
         const bool loaded=(CopyBuffer(atr_handle,0,shift,1,atr_buffer)==1 &&
                            atr_buffer[0]>0.0 &&
                            LoadPath(record.Symbol(),PERIOD_M15,shift,
                                     closes,highs,lows));
         CPricePathStateResult result;
         if(loaded)
            result=m_engine.Analyze(closes,highs,lows,atr_buffer[0]);

         bool row_written=false;
         if(!result.Valid)
            row_written=WriteNeutral(handle,record);
         else
            row_written=(FileWrite(
               handle,record.Id(),record.Timestamp(),
               result.PathDirectionalEfficiency,result.UpCloseRatio,
               result.DirectionalRunBalance,result.ReturnSignPersistence,
               result.PathTravelAtr,result.RangeEfficiency,
               result.RangeExpansion,100.0)>0);
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
            Print("Historical price path state export progress: ",
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
