//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : ExposureManager.mqh                                    |
//| Layer   : Money Management                                       |
//+------------------------------------------------------------------+

#ifndef CORE_MONEY_EXPOSUREMANAGER_MQH
#define CORE_MONEY_EXPOSUREMANAGER_MQH


class CExposureManager
{
private:

   double m_buyLots;
   double m_sellLots;
   double m_totalLots;
   double m_floatingProfit;


public:

   CExposureManager()
   {
      Reset();
   }


   void Reset()
   {
      m_buyLots = 0.0;
      m_sellLots = 0.0;
      m_totalLots = 0.0;
      m_floatingProfit = 0.0;
   }


   bool Refresh()
   {
      Reset();

      int total = PositionsTotal();

      for(int i = 0; i < total; i++)
      {
         ulong ticket = PositionGetTicket(i);

         if(ticket == 0)
            continue;


         if(!PositionSelectByTicket(ticket))
            continue;


         double volume =
            PositionGetDouble(POSITION_VOLUME);


         double profit =
            PositionGetDouble(POSITION_PROFIT);


         long type =
            PositionGetInteger(POSITION_TYPE);


         if(type == POSITION_TYPE_BUY)
            m_buyLots += volume;


         if(type == POSITION_TYPE_SELL)
            m_sellLots += volume;


         m_totalLots += volume;

         m_floatingProfit += profit;
      }


      return true;
   }


   double BuyLots()
   {
      return m_buyLots;
   }


   double SellLots()
   {
      return m_sellLots;
   }


   double TotalLots()
   {
      return m_totalLots;
   }


   double FloatingProfit()
   {
      return m_floatingProfit;
   }


   double ExposurePercent()
   {
      double balance =
         AccountInfoDouble(ACCOUNT_BALANCE);


      if(balance <= 0)
         return 0;


      return
      (m_totalLots / balance) * 100.0;
   }


   bool CanOpen(double maxExposurePercent)
   {
      return ExposurePercent() < maxExposurePercent;
   }

};


#endif