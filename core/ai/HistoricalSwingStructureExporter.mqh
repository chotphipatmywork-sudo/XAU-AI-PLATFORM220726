//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalSwingStructureExporter.mqh                   |
//| Layer   : Core / AI / Learning / Research                        |
//| Version : 1.0.0                                                  |
//| Purpose : Export confirmed M15 swing structure by Dataset row    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_HISTORICALSWINGSTRUCTUREEXPORTER_MQH
#define CORE_AI_HISTORICALSWINGSTRUCTUREEXPORTER_MQH

#include "storage/DatasetReader.mqh"
#include "../brain/trend/engines/ConfirmedSwingStructureEngine.mqh"

class CHistoricalSwingStructureExporter
  {
private:
   CConfirmedSwingStructureEngine m_engine;

   bool LoadRates(const string symbol,const ENUM_TIMEFRAMES timeframe,
                  const int shift,double &highs[],double &lows[],
                  double &closes[]) const
     {
      const int count=m_engine.RequiredBars();
      ArrayResize(highs,count);
      ArrayResize(lows,count);
      ArrayResize(closes,count);
      for(int index=0; index<count; index++)
        {
         const int source_shift=shift+index;
         highs[index]=iHigh(symbol,timeframe,source_shift);
         lows[index]=iLow(symbol,timeframe,source_shift);
         closes[index]=iClose(symbol,timeframe,source_shift);
         if(highs[index]<=0.0 || lows[index]<=0.0 || closes[index]<=0.0)
            return(false);
        }
      return(true);
     }

public:
   CHistoricalSwingStructureExporter(void)
     {
      m_engine.Configure(2,2,64);
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
      FileWrite(handle,"id","timestamp","structure_direction",
                "break_direction","choch_direction",
                "structure_range_position","structure_valid");

      int written=0;
      CDatasetRecord record;
      while(reader.Read(record))
        {
         const datetime observation=ObservationTime(record.Timestamp(),PERIOD_M15);
         const int shift=iBarShift(record.Symbol(),PERIOD_M15,record.Timestamp(),true);
         if(shift<0 || !IsBarClosed(record.Timestamp(),observation,PERIOD_M15))
           {
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         double highs[];
         double lows[];
         double closes[];
         if(!LoadRates(record.Symbol(),PERIOD_M15,shift,highs,lows,closes))
           {
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         const CConfirmedSwingStructureResult result=
            m_engine.Analyze(highs,lows,closes);
         if(FileWrite(handle,record.Id(),record.Timestamp(),
                      result.StructureDirection,result.BreakDirection,
                      result.ChochDirection,result.RangePosition,
                      (result.Valid ? 100.0 : 0.0))==0)
           {
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         written++;
         if(written%progress_interval==0)
           {
            FileFlush(handle);
            Print("Historical swing structure export progress: ",written," records");
           }
        }
      FileFlush(handle);
      FileClose(handle);
      reader.Shutdown();
      return(written);
     }
  };

#endif
