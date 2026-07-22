//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DailyLossTracker.mqh                                   |
//| Layer   : Risk                                                   |
//| Version : 1.1.0                                                  |
//| Purpose : Daily Loss Tracking                                    |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_DAILYLOSSTRACKER_MQH
#define CORE_RISK_DAILYLOSSTRACKER_MQH


class CDailyLossTracker
{
private:

    double m_startBalance;

    datetime m_dayStart;


public:


    CDailyLossTracker()
    {
        Reset();
    }



    void Reset()
    {
        m_startBalance = 0.0;

        m_dayStart = 0;
    }



    void Initialize()
    {
        m_startBalance =
            AccountInfoDouble(ACCOUNT_BALANCE);

        m_dayStart =
            TimeCurrent();
    }



    double GetDailyLossPercent()
    {
        double balance =
            AccountInfoDouble(ACCOUNT_BALANCE);


        if(m_startBalance <= 0.0)
            return 0.0;


        double loss =
            m_startBalance - balance;


        if(loss <= 0.0)
            return 0.0;


        return
            (loss / m_startBalance)
            * 100.0;
    }



    bool IsNewDay()
    {
        if(m_dayStart == 0)
            return true;


        MqlDateTime current;
        MqlDateTime start;


        TimeToStruct(
            TimeCurrent(),
            current);


        TimeToStruct(
            m_dayStart,
            start);



        return
        (
            current.day  != start.day ||
            current.mon  != start.mon ||
            current.year != start.year
        );
    }



    void Update()
    {
        if(IsNewDay())
        {
            Initialize();
        }
    }

};


#endif