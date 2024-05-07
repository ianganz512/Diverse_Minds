# python gen_gsm_new.py --agents 1 --rounds 2 --num_of_questions 500 --temperatures 0.7
# python gen_gsm_new.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.7 0.7 0.7
# python gen_gsm_new.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.6 0.7 0.8
python gen_gsm_new.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.5 0.7 0.9
# python gen_gsm_new.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.4 0.7 1.0

# do evaluation
python eval_gsm_judge.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.7 0.7 0.7
# python eval_gsm_judge.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.6 0.7 0.8
# python eval_gsm_judge.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.5 0.7 0.9
# python eval_gsm_judge.py --agents 3 --rounds 2 --num_of_questions 500 --temperatures 0.4 0.7 1.0
