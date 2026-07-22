//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HistoricalH1ContextExporter.mqh                        |
//| Layer   : Core / AI / Learning / Research                        |
//| Version : 1.0.0                                                  |
//| Purpose : Export past-only closed-H1 Brain context by timestamp  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_HISTORICALH1CONTEXTEXPORTER_MQH
#define CORE_AI_HISTORICALH1CONTEXTEXPORTER_MQH

#include "storage/DatasetReader.mqh"
#include "../brain/HistoricalBrainReplay.mqh"

class CHistoricalH1ContextExporter
  {
private:
   CHistoricalBrainReplay m_brain_replay;
   datetime               m_cached_h1_open;
   double                 m_trend_regime;
   double                 m_trend_momentum;
   double                 m_trend_slope;
   double                 m_volatility_regime;
   double                 m_volatility_change;

   bool IsBounded(const double value) const
     {
      return(value>=0.0 && value<=100.0);
     }

   int LastClosedH1Shift(const string symbol,const datetime observation_time) const
     {
      if(symbol=="" || observation_time<=0)
         return(-1);
      int shift=iBarShift(symbol,PERIOD_H1,observation_time-1,false);
      const int available=Bars(symbol,PERIOD_H1);
      while(shift>=0 && shift<available)
        {
         const datetime h1_open=iTime(symbol,PERIOD_H1,shift);
         if(h1_open>0 && IsHigherBarClosed(h1_open,observation_time))
            return(shift);
         shift++;
        }
      return(-1);
     }

   bool LoadContext(const string symbol,const datetime observation_time)
     {
      const int shift=LastClosedH1Shift(symbol,observation_time);
      if(shift<0)
         return(false);
      const datetime h1_open=iTime(symbol,PERIOD_H1,shift);
      if(h1_open<=0)
         return(false);
      if(h1_open==m_cached_h1_open)
         return(true);

      const CBrainAnalysisResult analysis=m_brain_replay.Analyze(symbol,PERIOD_H1,shift);
      if(!analysis.Valid)
         return(false);
      m_trend_regime=analysis.Trend.AITrendRegime;
      m_trend_momentum=analysis.Trend.AITrendMomentum;
      m_trend_slope=analysis.Trend.AITrendSlope;
      m_volatility_regime=analysis.Volatility.AIVolatilityRegime;
      m_volatility_change=analysis.Volatility.AIVolatilityChange;
      if(!IsBounded(m_trend_regime) || !IsBounded(m_trend_momentum) ||
         !IsBounded(m_trend_slope) || !IsBounded(m_volatility_regime) ||
         !IsBounded(m_volatility_change))
         return(false);
      m_cached_h1_open=h1_open;
      return(true);
     }

public:
   CHistoricalH1ContextExporter(void)
     {
      m_cached_h1_open=0;
      m_trend_regime=50.0;
      m_trend_momentum=50.0;
      m_trend_slope=50.0;
      m_volatility_regime=50.0;
      m_volatility_change=50.0;
     }

   datetime ObservationTime(const datetime bar_open,const ENUM_TIMEFRAMES timeframe) const
     {
      const int seconds=PeriodSeconds(timeframe);
      if(bar_open<=0 || seconds<=0)
         return(0);
      return(bar_open+seconds);
     }

   bool IsHigherBarClosed(const datetime higher_bar_open,const datetime observation_time) const
     {
      return(higher_bar_open>0 && observation_time>0 &&
             higher_bar_open+PeriodSeconds(PERIOD_H1)<=observation_time);
     }

   int Export(const string dataset_file,const string output_file,const int progress_interval=100)
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
      FileWrite(handle,"id","timestamp","h1_trend_regime","h1_trend_momentum",
                "h1_trend_slope","h1_volatility_regime","h1_volatility_change");

      int written=0;
      CDatasetRecord record;
      while(reader.Read(record))
        {
         const datetime observation_time=ObservationTime(record.Timestamp(),PERIOD_M15);
         if(observation_time<=0 || !LoadContext(record.Symbol(),observation_time))
           {
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         if(FileWrite(handle,record.Id(),record.Timestamp(),m_trend_regime,
                      m_trend_momentum,m_trend_slope,m_volatility_regime,
                      m_volatility_change)==0)
           {
            FileClose(handle);
            reader.Shutdown();
            return(-1);
           }
         written++;
         if(written%progress_interval==0)
           {
            FileFlush(handle);
            Print("Historical H1 context export progress: ",written," records");
           }
        }
      FileFlush(handle);
      FileClose(handle);
      reader.Shutdown();
      return(written);
     }
  };

#endif
