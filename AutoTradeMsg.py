# -*- coding: utf-8 -*-
'''
# 알고리즘 트래이딩 시스템
# Auth : tom17@kakao.com
# AutoTradeMsg.py
'''

import sys, asyncio, time
from datetime import datetime
import AutoTradingMyinfo as _t_myinfo
import AutoTradingSetting as _t_setting

def cal_profit():
    mystockinfos = _t_myinfo.get_acct_balance()
    tot_buy_cost = 0
    tot_sell_cost = 0
    tot_ticker_cnt = 0

    for r in mystockinfos.itertuples():
        b_cost = r.매입단가 * r.매도가능수량
        s_cost = r.현재가 * r.매도가능수량
        cnt = 1
        tot_buy_cost += b_cost
        tot_sell_cost += s_cost
        tot_ticker_cnt += cnt

    tot_profit = (tot_sell_cost - tot_buy_cost)
    tot_rate = tot_profit/tot_buy_cost * 100

    res_data = {
        "tot_ticker_cnt" : tot_ticker_cnt , 
        "tot_buy_cost" : tot_buy_cost,
        "tot_sell_cost" : tot_sell_cost,
        "tot_profit" : tot_profit,
        "tot_rate" : tot_rate
    }

    return mystockinfos , res_data

def make_msg(doc):

    msg = '[' + str(datetime.now()) + '] Daily Report - 투자종목수: ' \
    +str(doc['tot_ticker_cnt'])+'개, 총투자금액: '+str(doc['tot_buy_cost'])+'원 , 현재가: ' \
    +str(doc['tot_sell_cost'])+'원 , 총 수익금: '+str(doc['tot_profit'])+'월, 총 수익율: ' \
    +str(doc['tot_rate'])+'%'

    return msg

async def main():
    try:
        notwork_days = _t_setting._cfg['nodaylist']
        while True:
            # 거래 시간 정의
            t_now = datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
            today = datetime.today().weekday()
            holiday = datetime.today().strftime('%Y-%m-%d')
            _my_stock_infos_ , _summary_ = cal_profit()

            # 장이 열리지 않는 날은 Exit
            if holiday in notwork_days:
                _t_setting.send_slack_msg("#stock",'Today is Holiday')
                sys.exit(0)
            # 주말 , 주일은 Exit
            if today == 5 or today == 6:
                msg_week = 'Today is', 'Saturday.' if today == 5 else 'Sunday.'
                _t_setting.send_slack_msg("#stock", str(msg_week))
                sys.exit(0)
            # 09:00 ~ 15:15 주식 거래 시작
            if t_9 < t_now < t_sell:
                # 매시 30분 마다 프로세스 확인 메시지(슬랙)를 보낸다
                if t_now.minute == 30 and 0 <= t_now.second <=3:
                    _rate_ = _summary_['tot_rate']
                    if _rate_ >= 10:
                        _msg_ = make_msg(_summary_)
                        _t_setting.send_slack_msg("#stock",_msg_)
                time.sleep(1)
            # 15:20 ~                
            if t_exit < t_now:
                _t_setting.send_slack_msg("#stock",str(_my_stock_infos_))
                sys.exit(0)                
            time.sleep(3)
    except Exception as ex:
        msgout('`main -> exception! ' + str(ex) + '`')


if __name__ == '__main__':
    msgout = _t_setting.msgout
    _t_setting.auth(svr='prod',product='01')
    asyncio.run(main())