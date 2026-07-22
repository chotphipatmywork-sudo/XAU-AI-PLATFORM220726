//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ConfirmedSwingStructureEngine.mqh                      |
//| Layer   : Brain / Trend / Engines / Research                     |
//| Version : 1.0.0                                                  |
//| Purpose : Detect confirmed past-only swing structure             |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_ENGINES_CONFIRMEDSWINGSTRUCTUREENGINE_MQH
#define CORE_BRAIN_TREND_ENGINES_CONFIRMEDSWINGSTRUCTUREENGINE_MQH

#include "../models/ConfirmedSwingStructureResult.mqh"

class CConfirmedSwingStructureEngine
  {
private:
   int m_left_bars;
   int m_right_bars;
   int m_lookback;

   bool IsPivotHigh(const double &highs[],const int index) const
     {
      const double value=highs[index];
      for(int offset=1; offset<=m_right_bars; offset++)
         if(value<=highs[index-offset])
            return(false);
      for(int offset=1; offset<=m_left_bars; offset++)
         if(value<=highs[index+offset])
            return(false);
      return(true);
     }

   bool IsPivotLow(const double &lows[],const int index) const
     {
      const double value=lows[index];
      for(int offset=1; offset<=m_right_bars; offset++)
         if(value>=lows[index-offset])
            return(false);
      for(int offset=1; offset<=m_left_bars; offset++)
         if(value>=lows[index+offset])
            return(false);
      return(true);
     }

public:
   CConfirmedSwingStructureEngine(void)
     {
      m_left_bars=2;
      m_right_bars=2;
      m_lookback=64;
     }

   bool Configure(const int left_bars,const int right_bars,const int lookback)
     {
      if(left_bars<=0 || right_bars<=0 ||
         lookback<left_bars+right_bars+4)
         return(false);
      m_left_bars=left_bars;
      m_right_bars=right_bars;
      m_lookback=lookback;
      return(true);
     }

   int RequiredBars(void) const
     {
      return(m_lookback+m_left_bars+1);
     }

   CConfirmedSwingStructureResult Analyze(const double &highs[],
                                          const double &lows[],
                                          const double &closes[]) const
     {
      CConfirmedSwingStructureResult result;
      const int size=ArraySize(highs);
      if(size!=ArraySize(lows) || size!=ArraySize(closes) ||
         size<RequiredBars())
         return(result);

      double latest_high=0.0;
      double previous_high=0.0;
      double latest_low=0.0;
      double previous_low=0.0;
      int high_count=0;
      int low_count=0;
      const int final_index=MathMin(m_lookback,size-m_left_bars-1);

      for(int index=m_right_bars; index<=final_index; index++)
        {
         if(high_count<2 && IsPivotHigh(highs,index))
           {
            if(high_count==0)
               latest_high=highs[index];
            else
               previous_high=highs[index];
            high_count++;
           }
         if(low_count<2 && IsPivotLow(lows,index))
           {
            if(low_count==0)
               latest_low=lows[index];
            else
               previous_low=lows[index];
            low_count++;
           }
         if(high_count>=2 && low_count>=2)
            break;
        }

      if(high_count<2 || low_count<2 ||
         latest_high<=latest_low || previous_high<=0.0 || previous_low<=0.0)
         return(result);

      const bool bullish_structure=(latest_high>previous_high &&
                                    latest_low>previous_low);
      const bool bearish_structure=(latest_high<previous_high &&
                                    latest_low<previous_low);
      if(bullish_structure)
         result.StructureDirection=100.0;
      else if(bearish_structure)
         result.StructureDirection=0.0;

      const double close=closes[0];
      const bool bullish_break=(close>latest_high);
      const bool bearish_break=(close<latest_low);
      if(bullish_break && !bearish_break)
         result.BreakDirection=100.0;
      else if(bearish_break && !bullish_break)
         result.BreakDirection=0.0;

      if(bearish_structure && bullish_break)
         result.ChochDirection=100.0;
      else if(bullish_structure && bearish_break)
         result.ChochDirection=0.0;

      const double swing_range=latest_high-latest_low;
      result.RangePosition=MathMax(0.0,MathMin(100.0,
         100.0*(close-latest_low)/swing_range));
      result.LatestSwingHigh=latest_high;
      result.LatestSwingLow=latest_low;
      result.Valid=true;
      return(result);
     }
  };

#endif
