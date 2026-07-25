//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PastOnlyStructuralStopExporter.mqh                     |
//| Layer   : Core / AI / Learning / Offline Research                |
//| Version : 1.0.0                                                  |
//| Purpose : Export past-only same-side M5/M15 Stop ladders         |
//+------------------------------------------------------------------+

#ifndef CORE_AI_PASTONLYSTRUCTURALSTOPEXPORTER_MQH
#define CORE_AI_PASTONLYSTRUCTURALSTOPEXPORTER_MQH

#include "PastOnlyStructuralTargetExporter.mqh"

class CPastOnlyStructuralStopExporter
  {
private:
   CPastOnlyStructuralTargetExporter m_ladder;

   bool Header(const int handle) const
     {
      const string expected[]={
         "request_schema_version","request_id","source","observation_time",
         "symbol","direction","entry_bar_open","expected_entry",
         "entry_known","structural_stop","current_target",
         "estimated_cost_points","cost_known","minimum_rr"
      };
      for(int i=0;i<ArraySize(expected);i++)
         if(FileReadString(handle)!=expected[i])
            return(false);
      return(true);
     }

   bool Boolean(const string text,bool &value) const
     {
      if(text=="true") { value=true; return(true); }
      if(text=="false") { value=false; return(true); }
      return(false);
     }

   int Abort(const int input_handle,const int output_handle,const string file,
             const string reason) const
     {
      if(input_handle!=INVALID_HANDLE) FileClose(input_handle);
      if(output_handle!=INVALID_HANDLE) FileClose(output_handle);
      if(FileIsExist(file)) FileDelete(file);
      Print("Past-only structural Stop export failed closed: ",reason);
      return(-1);
     }

   bool Rates(const string symbol,const ENUM_TIMEFRAMES timeframe,
              const datetime latest,const datetime observation,
              double &highs[],double &lows[]) const
     {
      const int required=m_ladder.RequiredBars();
      MqlRates rates[];
      int copied=-1;
      for(int attempt=0;attempt<40;attempt++)
        {
         copied=CopyRates(symbol,timeframe,latest,required,rates);
         if(copied>=required) break;
         Sleep(250);
        }
      const int shift=iBarShift(symbol,timeframe,latest,true);
      if(copied<required || shift<0 || iTime(symbol,timeframe,shift)!=latest)
         return(false);
      ArrayResize(highs,required);
      ArrayResize(lows,required);
      const int seconds=PeriodSeconds(timeframe);
      for(int i=0;i<required;i++)
        {
         const int source=shift+i;
         const datetime open=iTime(symbol,timeframe,source);
         highs[i]=iHigh(symbol,timeframe,source);
         lows[i]=iLow(symbol,timeframe,source);
         if(open<=0 || open+seconds>observation || highs[i]<lows[i] ||
            lows[i]<=0.0)
            return(false);
        }
      return(true);
     }

   double Slot(const double &values[],const int index) const
     {
      return(index<ArraySize(values) ? values[index] : 0.0);
     }

public:
   int RequiredBars(void) const
     {
      return(m_ladder.RequiredBars());
     }

   int BuildStopLadder(const double entry,const bool buy,
                       const double &highs[],const double &lows[],
                       const double point,double &stops[]) const
     {
      return(m_ladder.BuildTargetLadder(entry,!buy,highs,lows,point,stops));
     }

   int Export(const string request_file,const string output_file,
              const int progress_interval=50)
     {
      const int input_handle=FileOpen(request_file,FILE_CSV|FILE_READ|FILE_ANSI,',');
      if(input_handle==INVALID_HANDLE) return(-1);
      if(!Header(input_handle)) return(Abort(input_handle,INVALID_HANDLE,output_file,
                                     "request schema mismatch"));
      if(FileIsExist(output_file) && !FileDelete(output_file))
         return(Abort(input_handle,INVALID_HANDLE,output_file,"old output retained"));
      const int output=FileOpen(output_file,FILE_CSV|FILE_WRITE|FILE_ANSI,',');
      if(output==INVALID_HANDLE) return(Abort(input_handle,output,output_file,
                                             "output unavailable"));
      FileWrite(output,"export_schema_version","request_id","observation_time",
                "symbol","direction","entry","current_stop","current_target",
                "estimated_cost_points","cost_known","minimum_rr",
                "m5_stop_1","m5_stop_2","m5_stop_3","m5_stop_count",
                "m15_stop_1","m15_stop_2","m15_stop_3","m15_stop_count",
                "known_time_valid","deployment_authorized");
      int written=0;
      while(!FileIsEnding(input_handle))
        {
         const string schema=FileReadString(input_handle);
         if(schema=="" && FileIsEnding(input_handle)) break;
         const string id=FileReadString(input_handle);
         FileReadString(input_handle);
         const string observation_text=FileReadString(input_handle);
         const string symbol=FileReadString(input_handle);
         const string direction=FileReadString(input_handle);
         const string entry_open_text=FileReadString(input_handle);
         const double expected_entry=StringToDouble(FileReadString(input_handle));
         const string entry_known_text=FileReadString(input_handle);
         const double current_stop=StringToDouble(FileReadString(input_handle));
         const double current_target=StringToDouble(FileReadString(input_handle));
         const double cost=StringToDouble(FileReadString(input_handle));
         const string cost_known_text=FileReadString(input_handle);
         const double minimum_rr=StringToDouble(FileReadString(input_handle));
         bool entry_known=false,cost_known=false;
         const datetime observation=StringToTime(observation_text);
         const datetime entry_open=StringToTime(entry_open_text);
         const bool buy=(direction=="TRADE_SETUP_BUY");
         if(schema!="1.0.0" || id=="" || symbol!="XAUUSD" ||
            (!buy && direction!="TRADE_SETUP_SELL") ||
            !Boolean(entry_known_text,entry_known) ||
            !Boolean(cost_known_text,cost_known) || observation<=0 ||
            entry_open+PeriodSeconds(PERIOD_M5)!=observation ||
            current_stop<=0.0 || current_target<=0.0 || cost<0.0 ||
            minimum_rr<2.0)
            return(Abort(input_handle,output,output_file,"malformed request "+id));
         const int shift=iBarShift(symbol,PERIOD_M5,entry_open,true);
         if(shift<0) return(Abort(input_handle,output,output_file,
                                 "trigger unavailable "+id));
         const double entry=iClose(symbol,PERIOD_M5,shift);
         const double point=SymbolInfoDouble(symbol,SYMBOL_POINT);
         if(entry<=0.0 || point<=0.0 ||
            (entry_known && MathAbs(entry-expected_entry)>point*0.5))
            return(Abort(input_handle,output,output_file,"Entry parity "+id));
         double h5[],l5[],h15[],l15[];
         if(!Rates(symbol,PERIOD_M5,entry_open,observation,h5,l5) ||
            !Rates(symbol,PERIOD_M15,observation-PeriodSeconds(PERIOD_M15),
                   observation,h15,l15))
            return(Abort(input_handle,output,output_file,"history unavailable "+id));
         double s5[],s15[];
         const int c5=BuildStopLadder(entry,buy,h5,l5,point,s5);
         const int c15=BuildStopLadder(entry,buy,h15,l15,point,s15);
         if(c5<0 || c15<0)
            return(Abort(input_handle,output,output_file,"Stop ladder failed "+id));
         FileWrite(output,"1.0.0",id,observation_text,symbol,direction,entry,
                   current_stop,current_target,cost,
                   (cost_known?"true":"false"),minimum_rr,
                   Slot(s5,0),Slot(s5,1),Slot(s5,2),c5,
                   Slot(s15,0),Slot(s15,1),Slot(s15,2),c15,"true","false");
         written++;
         if(written%progress_interval==0)
            Print("Past-only structural Stop export progress: ",written);
        }
      FileClose(input_handle);
      FileClose(output);
      return(written);
     }
  };
#endif
