# Probe items to hand-check

For each item, check that the gold answer is right for the shown wording, and that a negated or renamed version
says what it should. Mark problems in the last line of an item. States are cut at 320 characters.

## A. Name swap

Each question appears twice: names bound to their usual meaning (aligned), then swapped. The gold answer must follow the definition, so it changes name between the two arms.

### A1. agnews_yn (kev_seen: reject/accept)

> Sun Sets Sights on Linux Vendors (AP) AP - After years of battling Microsoft Corp., Sun Microsystems Inc. has set its sights on Linux vendors, seeking to jump into a low-end but high-volume market it's been accused of ignoring.

**Question:** Is this article about science and technology?

- aligned: `reject`: The article is mainly about a different topic; `accept`: The article is mainly about science and technology  **gold: `accept`**
- swapped: `reject`: The article is mainly about science and technology; `accept`: The article is mainly about a different topic  **gold: `reject`**
- check: OK / problem:

### A2. composition_atom (heldout: denied/approved)

> {'policy': 'Approve exactly when account value is greater than 35. Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The account value is 46. The routing reference is 953.'}

**Question:** Apply the policy to this case.

- aligned: `denied`: The policy does not permit this case; `approved`: The policy permits this case  **gold: `approved`**
- swapped: `denied`: The policy permits this case; `approved`: The policy does not permit this case  **gold: `denied`**
- check: OK / problem:

### A3. composition_conditional (random_test: mxlqv/dkzrw)

> {'policy': 'Approve exactly when if (entry value is at most 53), use (request value is less than 31); otherwise use (case value is less than 22). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The routing reference is 110. The entry value is 53. The case value is 23. The request value is  ...

**Question:** Apply the policy to this case.

- aligned: `mxlqv`: The policy does not permit this case; `dkzrw`: The policy permits this case  **gold: `dkzrw`**
- swapped: `mxlqv`: The policy permits this case; `dkzrw`: The policy does not permit this case  **gold: `mxlqv`**
- check: OK / problem:

### A4. composition_conjunction (a1_train: false/true)

> {'policy': 'Approve exactly when (case value is greater than 49) AND (shipment verified is yes). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The shipment verified is yes. The routing reference is 136. The case value is 49.'}

**Question:** Apply the policy to this case.

- aligned: `false`: The policy does not permit this case; `true`: The policy permits this case  **gold: `false`**
- swapped: `false`: The policy permits this case; `true`: The policy does not permit this case  **gold: `true`**
- check: OK / problem:

### A5. composition_disjunction (heldout: denied/approved)

> {'policy': 'Approve exactly when (shipment signer is the same person as shipment designated approver) OR (case value is between 6 and 16, including both endpoints). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The routing reference is 101. The shipment signer is Mira. The case value is  ...

**Question:** Apply the policy to this case.

- aligned: `denied`: The policy does not permit this case; `approved`: The policy permits this case  **gold: `denied`**
- swapped: `denied`: The policy permits this case; `approved`: The policy does not permit this case  **gold: `approved`**
- check: OK / problem:

### A6. composition_exception (random_test: mxlqv/dkzrw)

> {'policy': 'Approve exactly when (member value is greater than 33) holds and the exception (package value is at most 22) does not hold. Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The package value is 32. The routing reference is 400. The member value is 34.'}

**Question:** Apply the policy to this case.

- aligned: `mxlqv`: The policy does not permit this case; `dkzrw`: The policy permits this case  **gold: `dkzrw`**
- swapped: `mxlqv`: The policy permits this case; `dkzrw`: The policy does not permit this case  **gold: `mxlqv`**
- check: OK / problem:

### A7. composition_held_and_or (random_test: qzvkm/trbxl)

> {'policy': 'Approve exactly when both these conditions hold: [(at least one of these conditions hold: [(member value is at least 60); (entry signer is the same person as entry designated approver)]); (review value is between 27 and 37, including both endpoints)]. Otherwise deny. The routing reference does not affect el ...

**Question:** Apply the policy to this case.

- aligned: `qzvkm`: The policy does not permit this case; `trbxl`: The policy permits this case  **gold: `qzvkm`**
- swapped: `qzvkm`: The policy permits this case; `trbxl`: The policy does not permit this case  **gold: `trbxl`**
- check: OK / problem:

### A8. composition_held_conditional (a1_train: fail/pass)

> {'policy': 'Approve exactly when if (account value is between 38 and 48, including both endpoints), use (it is not the case that (the elapsed days from package start date to package end date are at most 5)); otherwise use (request value is equal to 57). Otherwise deny. The routing reference does not affect eligibility. ...

**Question:** Apply the policy to this case.

- aligned: `fail`: The policy does not permit this case; `pass`: The policy permits this case  **gold: `fail`**
- swapped: `fail`: The policy permits this case; `pass`: The policy does not permit this case  **gold: `pass`**
- check: OK / problem:

### A9. composition_held_or_not (random_test: mxlqv/dkzrw)

> {'policy': 'Approve exactly when at least one of these conditions hold: [(both these conditions hold: [(the elapsed days from member start date to member end date are at most 5); (entry signer is the same person as entry designated approver)]); (it is not the case that (request value is less than 40))]. Otherwise deny. ...

**Question:** Apply the policy to this case.

- aligned: `mxlqv`: The policy does not permit this case; `dkzrw`: The policy permits this case  **gold: `dkzrw`**
- swapped: `mxlqv`: The policy permits this case; `dkzrw`: The policy does not permit this case  **gold: `mxlqv`**
- check: OK / problem:

### A10. composition_negation (kev_seen: no/yes)

> {'policy': 'Approve exactly when NOT (shipment verified is yes). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The shipment verified is no. The routing reference is 628.'}

**Question:** Apply the policy to this case.

- aligned: `no`: The policy does not permit this case; `yes`: The policy permits this case  **gold: `yes`**
- swapped: `no`: The policy permits this case; `yes`: The policy does not permit this case  **gold: `no`**
- check: OK / problem:

### A11. composition_nested_and (heldout: denied/approved)

> {'policy': 'Approve exactly when both these conditions hold: [(both these conditions hold: [(package value is less than 23); (shipment value is at most 24)]); (case value is greater than 59)]. Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The routing reference is 295. The case value is 7 ...

**Question:** Apply the policy to this case.

- aligned: `denied`: The policy does not permit this case; `approved`: The policy permits this case  **gold: `approved`**
- swapped: `denied`: The policy permits this case; `approved`: The policy does not permit this case  **gold: `denied`**
- check: OK / problem:

### A12. composition_nested_or (neutral: 0/1)

> {'policy': 'Approve exactly when (member value is greater than 46) OR ((account value is at least 25) OR (package value is between 25 and 35, including both endpoints)). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The routing reference is 679. The package value is 24. The member value  ...

**Question:** Apply the policy to this case.

- aligned: `0`: The policy does not permit this case; `1`: The policy permits this case  **gold: `0`**
- swapped: `0`: The policy permits this case; `1`: The policy does not permit this case  **gold: `1`**
- check: OK / problem:

### A13. contrastive_age_eligibility (heldout: denied/approved)

> {'policy': 'Applicants must be at least 16 years old to be eligible for the rental agreement.', 'case': 'The application form was complete and signed. Priya applied to join the rental agreement. Priya is 33 years old.'}

**Question:** Is the applicant eligible?

- aligned: `denied`: The applicant fails the policy's eligibility rules; `approved`: The applicant meets the policy's eligibility rules  **gold: `approved`**
- swapped: `denied`: The applicant meets the policy's eligibility rules; `approved`: The applicant fails the policy's eligibility rules  **gold: `denied`**
- check: OK / problem:

### A14. contrastive_authorization (kev_seen: reject/accept)

> {'policy': 'A refund is authorized only when its sole authorization was signed by someone who may authorize refunds for that account.', 'case': 'The refund amount is $40. Only Sana may authorize refunds for account 41. The sole authorization for this refund on account 41 was signed by Sana.'}

**Question:** Is the refund authorized?

- aligned: `reject`: The policy withholds authorization for the refund; `accept`: The policy authorizes the refund  **gold: `accept`**
- swapped: `reject`: The policy authorizes the refund; `accept`: The policy withholds authorization for the refund  **gold: `reject`**
- check: OK / problem:

### A15. contrastive_return_window (neutral: P/Q)

> {'policy': 'Returns are accepted only if the return request is submitted within 60 days of the purchase date.', 'case': "The order was paid by card and shipped to Lena's home address. The return request was submitted on July 6, 2026. Lena bought a rain jacket on April 27, 2026."}

**Question:** Is this return request within the policy window?

- aligned: `P`: The request falls outside the policy's return window; `Q`: The request falls inside the policy's return window  **gold: `P`**
- swapped: `P`: The request falls inside the policy's return window; `Q`: The request falls outside the policy's return window  **gold: `Q`**
- check: OK / problem:

### A16. imdb (neutral: P/Q)

> Another in the long line of Conan wannabes that tired to cash in on that movie's success, this Italian monstrosity is about as bad as they came. You know it's a bad sign when your heroes fight invisible enemies because the movie was made so cheaply there wasn't money for either adequate special effects or to hire real  ...

**Question:** Is this movie review positive?

- aligned: `P`: The reviewer disliked the film overall; `Q`: The reviewer liked the film overall  **gold: `P`**
- swapped: `P`: The reviewer liked the film overall; `Q`: The reviewer disliked the film overall  **gold: `Q`**
- check: OK / problem:

### A17. paws (neutral: 0/1)

> {'document': 'The miniseries was nominated for various awards and won , including several Primetime Emmy Awards and the Golden Globe Awards .'}

**Question:** Does this sentence mean the same thing: "The miniseries was nominated for and won various awards , including multiple Primetime Emmy Awards and Golden Globe Awards ."

- aligned: `0`: Different meaning, even if most words match; `1`: Same meaning, possibly reworded  **gold: `1`**
- swapped: `0`: Same meaning, possibly reworded; `1`: Different meaning, even if most words match  **gold: `0`**
- check: OK / problem:

### A18. qnli (heldout: absent/present)

> The largest of these is the Eldon Square Shopping Centre, one of the largest city centre shopping complexes in the UK.

**Question:** Does the sentence contain the answer to this question: "What is one of the largest city center shopping complexes in the UK?"

- aligned: `absent`: The sentence lacks the answer to the question; `present`: The sentence contains the answer to the question  **gold: `present`**
- swapped: `absent`: The sentence contains the answer to the question; `present`: The sentence lacks the answer to the question  **gold: `absent`**
- check: OK / problem:

### A19. tweet_offensive (random_test: wjfyd/hnpcg)

> #MAGA Alert : Joe Biden on #Trump Supporters: 'The Dregs Of Society' (VIDEO) via @user

**Question:** Is this post offensive?

- aligned: `wjfyd`: Not offensive; `hnpcg`: Contains insults, threats, profanity directed at someone, or hateful content  **gold: `wjfyd`**
- swapped: `wjfyd`: Contains insults, threats, profanity directed at someone, or hateful content; `hnpcg`: Not offensive  **gold: `hnpcg`**
- check: OK / problem:

### A20. yelp_yn (random_test: qzvkm/trbxl)

> My return visit to Rachel's Kitchen! I arrived just around 11:20 AM on a Saturday morning and the place was bustling, although not overly packed. The outside dining area had pretty much every table full of Summerlin moms and a scattering of elderly people and young people enjoying brunch or just coffee outside in the n ...

**Question:** Would this reviewer recommend the business?

- aligned: `qzvkm`: Negative or mixed; `trbxl`: Clearly positive overall  **gold: `qzvkm`**
- swapped: `qzvkm`: Clearly positive overall; `trbxl`: Negative or mixed  **gold: `trbxl`**
- check: OK / problem:

### A21. agnews_yn (neutral: P/Q)

> Donald Leads by Two in Dunhill Links (AP) AP - Luke Donald shot a 4-under-par 68 Saturday for a two-stroke lead after three rounds of the Dunhill Links Championship.

**Question:** Is this article about sports?

- aligned: `P`: The article is mainly about a different topic; `Q`: The article is mainly about sports  **gold: `Q`**
- swapped: `P`: The article is mainly about sports; `Q`: The article is mainly about a different topic  **gold: `P`**
- check: OK / problem:

### A22. composition_atom (neutral: P/Q)

> {'policy': 'Approve exactly when case value is equal to 27. Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The routing reference is 437. The case value is 26.'}

**Question:** Apply the policy to this case.

- aligned: `P`: The policy does not permit this case; `Q`: The policy permits this case  **gold: `P`**
- swapped: `P`: The policy permits this case; `Q`: The policy does not permit this case  **gold: `Q`**
- check: OK / problem:

### A23. composition_conditional (a1_train: false/true)

> {'policy': 'Approve exactly when if (entry value is at most 53), use (request value is less than 31); otherwise use (case value is less than 22). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The routing reference is 110. The entry value is 54. The case value is 23. The request value is  ...

**Question:** Apply the policy to this case.

- aligned: `false`: The policy does not permit this case; `true`: The policy permits this case  **gold: `false`**
- swapped: `false`: The policy permits this case; `true`: The policy does not permit this case  **gold: `true`**
- check: OK / problem:

### A24. composition_conjunction (random_test: mxlqv/dkzrw)

> {'policy': 'Approve exactly when (shipment value is at least 56) AND (member value is between 52 and 62, including both endpoints). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The shipment value is 55. The routing reference is 109. The member value is 53.'}

**Question:** Apply the policy to this case.

- aligned: `mxlqv`: The policy does not permit this case; `dkzrw`: The policy permits this case  **gold: `mxlqv`**
- swapped: `mxlqv`: The policy permits this case; `dkzrw`: The policy does not permit this case  **gold: `dkzrw`**
- check: OK / problem:

### A25. composition_disjunction (kev_seen: reject/accept)

> {'policy': 'Approve exactly when (member signer is the same person as member designated approver) OR (entry verified is yes). Otherwise deny. The routing reference does not affect eligibility.', 'case': 'The routing reference is 183. The entry verified is yes. The member designated approver is Tomas. The member signer  ...

**Question:** Apply the policy to this case.

- aligned: `reject`: The policy does not permit this case; `accept`: The policy permits this case  **gold: `accept`**
- swapped: `reject`: The policy permits this case; `accept`: The policy does not permit this case  **gold: `reject`**
- check: OK / problem:

## B. Negated questions

The original wording, then each negated style (S3 is held out of training). The gold flips under negation. Where a question has yes/no definitions, they swap too.

### B1. agnews_yn

> Cisco Flaw Leaves Router Vulnerable to Attack Cisco Systems issued a security advisory warning that some networks using its routers may be vulnerable to denial-of-service attacks. Devices running Internetwork Operating System and enabled for the open shortest path first (OSPF) ...

- orig: Is this article about science and technology?  **gold: yes**
- S1: Is this article not about science and technology?  **gold: no**
- S2: Is it false that this article is about science and technology?  **gold: no**
- S3: Is this article about a topic other than science and technology?  **gold: no**
- check: OK / problem:

### B2. contrastive_age_eligibility

> {'policy': 'Applicants must be at least 25 years old to be eligible for the rental agreement.', 'case': 'Jonas is 20 years old. The application form was complete and signed. Jonas applied to join the rental agreement.'}

- orig: Is the applicant eligible?  **gold: no**
- S1: Is the applicant not eligible?  **gold: yes**
- S2: Is it false that the applicant is eligible?  **gold: yes**
- S3: Is the applicant ineligible?  **gold: yes**
- check: OK / problem:

### B3. contrastive_authorization

> {'policy': 'A refund is authorized only when its sole authorization was signed by someone who may authorize refunds for that account.', 'case': 'Only Aiko may authorize refunds for account 28. The refund amount is $350. The sole authorization for this refund on account 28 was signed by Kofi.'}

- orig: Is the refund authorized?  **gold: no**
- S1: Is the refund not authorized?  **gold: yes**
- S2: Is it false that the refund is authorized?  **gold: yes**
- S3: Is the refund unauthorized?  **gold: yes**
- check: OK / problem:

### B4. contrastive_return_window

> {'policy': 'Returns are accepted only if the return request is submitted within 45 days of the purchase date.', 'case': "The order was paid by card and shipped to Noah's home address. Noah bought a desk lamp on August 16, 2026. The return request was submitted on October 11, 2026."}

- orig: Is this return request within the policy window?  **gold: no**
- S1: Is this return request not within the policy window?  **gold: yes**
- S2: Is it false that this return request is within the policy window?  **gold: yes**
- S3: Is this return request outside the policy window?  **gold: yes**
- check: OK / problem:

### B5. imdb

> I didn't really concentrate on the larger Genocidal aspects of the story (although the horrific images at the beginning are very powerful). I was really taken with the human story of the girl and her family. Imagine living your life not knowing if you have a time bomb ticking away inside you. I was really wrenching to  ...

- orig: Is this movie review positive?  **gold: yes** (yes = The reviewer liked the film overall; no = The reviewer disliked the film overall)
- S1: Is this movie review not positive?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- S2: Is it false that this movie review is positive?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- S3: Did the reviewer dislike the film overall?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- check: OK / problem:

### B6. paws

> The ITSEC has been largely replaced by Common Criteria , which provides similarly-defined evaluation levels and implements the target of evaluation concept and the Security Target document .

- orig: Does this sentence mean the same thing: "ITSEC has been largely replaced by Common Criteria , which provides similarly defined evaluation levels and implements the goal of the evaluation concept and the security target document ."  **gold: yes** (yes = Same meaning, possibly reworded; no = Different meaning, even if most words match)
- S1: Does this sentence not mean the same thing: "ITSEC has been largely replaced by Common Criteria , which provides similarly defined evaluation levels and implements the goal of the evaluation concept and the security target document ."  **gold: no** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- S2: Is it false that this sentence means the same thing: "ITSEC has been largely replaced by Common Criteria , which provides similarly defined evaluation levels and implements the goal of the evaluation concept and the security target document ."  **gold: no** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- S3: Does this sentence mean something different from: "ITSEC has been largely replaced by Common Criteria , which provides similarly defined evaluation levels and implements the goal of the evaluation concept and the security target document ."  **gold: no** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- check: OK / problem:

### B7. qnli

> {'ticket': {'channel': 'web form', 'body': 'It stands alone in sending manned missions beyond low Earth orbit.'}}

- orig: Does the sentence contain the answer to this question: "What Apollo mission was the sixth moon landing?"  **gold: no**
- S1: Does the sentence not contain the answer to this question: "What Apollo mission was the sixth moon landing?"  **gold: yes**
- S2: Is it false that the sentence contains the answer to this question: "What Apollo mission was the sixth moon landing?"  **gold: yes**
- S3: Is the sentence missing the answer to this question: "What Apollo mission was the sixth moon landing?"  **gold: yes**
- check: OK / problem:

### B8. tweet_offensive

> #Investment #Leadership #Preparation thx @user for sharing yr #InfrastructureReportCard and guidance at @user #MAGA or watch it rust away...

- orig: Is this post offensive?  **gold: no** (yes = Contains insults, threats, profanity directed at someone, or hateful content; no = Not offensive)
- S1: Is this post not offensive?  **gold: yes** (yes = Not offensive; no = Contains insults, threats, profanity directed at someone, or hateful content)
- S2: Is it false that this post is offensive?  **gold: yes** (yes = Not offensive; no = Contains insults, threats, profanity directed at someone, or hateful content)
- S3: Is this post free of offensive content?  **gold: yes** (yes = Not offensive; no = Contains insults, threats, profanity directed at someone, or hateful content)
- check: OK / problem:

### B9. yelp_yn

> [{'role': 'customer', 'content': "Don't come here before 10 pm on a Friday night unless you want to listen to old ladies singing oldies songs. We were a fun group that stopped in at 8:30ish to listen to some karaoke, and it was a disaster. A bunch of blue hairs reliving their glory days and terrorizing the ears of ever ...

- orig: Would this reviewer recommend the business?  **gold: no** (yes = Clearly positive overall; no = Negative or mixed)
- S1: Would this reviewer not recommend the business?  **gold: yes** (yes = Negative or mixed; no = Clearly positive overall)
- S2: Is it false that this reviewer would recommend the business?  **gold: yes** (yes = Negative or mixed; no = Clearly positive overall)
- S3: Is this reviewer's overall view of the business negative or mixed?  **gold: yes** (yes = Negative or mixed; no = Clearly positive overall)
- check: OK / problem:

### B10. agnews_yn

> Good Luck and Bubblewrap.com Collard greens and black-eyed peas, a New Years tradition, on a chefs site; Virtual-Bubblewrap.com lets you punch holes with your mouse; KnowItAllVideo.com, where amateur instructional videos are posted and rated.

- orig: Is this article about science and technology?  **gold: yes**
- S1: Is this article not about science and technology?  **gold: no**
- S2: Is it false that this article is about science and technology?  **gold: no**
- S3: Is this article about a topic other than science and technology?  **gold: no**
- check: OK / problem:

### B11. contrastive_age_eligibility

> {'policy': 'Applicants must be at least 16 years old to be eligible for the rental agreement.', 'case': 'The application form was complete and signed. Priya applied to join the rental agreement. Priya is 33 years old.'}

- orig: Is the applicant eligible?  **gold: yes**
- S1: Is the applicant not eligible?  **gold: no**
- S2: Is it false that the applicant is eligible?  **gold: no**
- S3: Is the applicant ineligible?  **gold: no**
- check: OK / problem:

### B12. contrastive_authorization

> {'policy': 'A refund is authorized only when its sole authorization was signed by someone who may authorize refunds for that account.', 'case': 'The refund amount is $40. The sole authorization for this refund on account 22 was signed by Aiko. Only Aiko may authorize refunds for account 22.'}

- orig: Is the refund authorized?  **gold: yes**
- S1: Is the refund not authorized?  **gold: no**
- S2: Is it false that the refund is authorized?  **gold: no**
- S3: Is the refund unauthorized?  **gold: no**
- check: OK / problem:

### B13. contrastive_return_window

> {'policy': 'Returns are accepted only if the return request is submitted within 60 days of the purchase date.', 'case': "The order was paid by card and shipped to Mira's home address. The return request was submitted on June 27, 2026. Mira bought a desk lamp on June 3, 2026."}

- orig: Is this return request within the policy window?  **gold: yes**
- S1: Is this return request not within the policy window?  **gold: no**
- S2: Is it false that this return request is within the policy window?  **gold: no**
- S3: Is this return request outside the policy window?  **gold: no**
- check: OK / problem:

### B14. imdb

> Hollywood has turned the Mafia in to a production line of output ranging from the banal to the excellent and despite some good acting and a reasonable script (much of which is - for a change - true!) this "home entertainment" effort has to fall slap bang in the middle. The script is not only obvious (all of the checkli ...

- orig: Is this movie review positive?  **gold: yes** (yes = The reviewer liked the film overall; no = The reviewer disliked the film overall)
- S1: Is this movie review not positive?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- S2: Is it false that this movie review is positive?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- S3: Did the reviewer dislike the film overall?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- check: OK / problem:

### B15. paws

> Julian Wehr ( 1898 -- 1970 ) was known as the `` Animated Master of American Books '' .

- orig: Does this sentence mean the same thing: "Julian Wehr ( 1898 - 1970 ) was known as the `` Animated Master of American Books '' ."  **gold: yes** (yes = Same meaning, possibly reworded; no = Different meaning, even if most words match)
- S1: Does this sentence not mean the same thing: "Julian Wehr ( 1898 - 1970 ) was known as the `` Animated Master of American Books '' ."  **gold: no** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- S2: Is it false that this sentence means the same thing: "Julian Wehr ( 1898 - 1970 ) was known as the `` Animated Master of American Books '' ."  **gold: no** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- S3: Does this sentence mean something different from: "Julian Wehr ( 1898 - 1970 ) was known as the `` Animated Master of American Books '' ."  **gold: no** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- check: OK / problem:

### B16. qnli

> U.S. Defense Secretary Robert Gates called for establishing something similar to the defunct U.S. Information Agency, which was charged with undermining the communist ideology during the Cold War.

- orig: Does the sentence contain the answer to this question: "What department in the U.S. spearheaded the efforts against Islamism?"  **gold: no**
- S1: Does the sentence not contain the answer to this question: "What department in the U.S. spearheaded the efforts against Islamism?"  **gold: yes**
- S2: Is it false that the sentence contains the answer to this question: "What department in the U.S. spearheaded the efforts against Islamism?"  **gold: yes**
- S3: Is the sentence missing the answer to this question: "What department in the U.S. spearheaded the efforts against Islamism?"  **gold: yes**
- check: OK / problem:

### B17. tweet_offensive

> #Kavanaugh The moment #BlaseyFord is exposed as a fraud, expect a new accuser to surface. Liberals are a one trick pony. #LiberalismIsAMentalDisorder

- orig: Is this post offensive?  **gold: yes** (yes = Contains insults, threats, profanity directed at someone, or hateful content; no = Not offensive)
- S1: Is this post not offensive?  **gold: no** (yes = Not offensive; no = Contains insults, threats, profanity directed at someone, or hateful content)
- S2: Is it false that this post is offensive?  **gold: no** (yes = Not offensive; no = Contains insults, threats, profanity directed at someone, or hateful content)
- S3: Is this post free of offensive content?  **gold: no** (yes = Not offensive; no = Contains insults, threats, profanity directed at someone, or hateful content)
- check: OK / problem:

### B18. yelp_yn

> {'document': "Stopped by here to get a drink before eating out. The place was loud, very loud. Loud from people shouting at the big screens (not sure, something with men on ice skates!), loud from birthday parties all over the place, and loud from the loud music playing. \\nIt's mainly a gin bar, so don't expect anythi ...

- orig: Would this reviewer recommend the business?  **gold: no** (yes = Clearly positive overall; no = Negative or mixed)
- S1: Would this reviewer not recommend the business?  **gold: yes** (yes = Negative or mixed; no = Clearly positive overall)
- S2: Is it false that this reviewer would recommend the business?  **gold: yes** (yes = Negative or mixed; no = Clearly positive overall)
- S3: Is this reviewer's overall view of the business negative or mixed?  **gold: yes** (yes = Negative or mixed; no = Clearly positive overall)
- check: OK / problem:

### B19. agnews_yn

> Australia Babcock amp; Brown To Pursue Listed Investment Co SYDNEY (Dow Jones)--Babcock amp; Brown Ltd. (BNB.AU) said Monday it plans to raise as much as A\$1 billion for an externally managed investment company to target long-term investments.

- orig: Is this article about business?  **gold: yes**
- S1: Is this article not about business?  **gold: no**
- S2: Is it false that this article is about business?  **gold: no**
- S3: Is this article about a topic other than business?  **gold: no**
- check: OK / problem:

### B20. contrastive_age_eligibility

> {'policy': 'Applicants must be at least 25 years old to be eligible for the rental agreement.', 'case': 'The application form was complete and signed. Priya applied to join the rental agreement. Priya is 27 years old.'}

- orig: Is the applicant eligible?  **gold: yes**
- S1: Is the applicant not eligible?  **gold: no**
- S2: Is it false that the applicant is eligible?  **gold: no**
- S3: Is the applicant ineligible?  **gold: no**
- check: OK / problem:

### B21. contrastive_authorization

> {'policy': 'A refund is authorized only when its sole authorization was signed by someone who may authorize refunds for that account.', 'case': 'Only Priya may authorize refunds for account 18. The refund amount is $900. The sole authorization for this refund on account 18 was signed by Priya.'}

- orig: Is the refund authorized?  **gold: yes**
- S1: Is the refund not authorized?  **gold: no**
- S2: Is it false that the refund is authorized?  **gold: no**
- S3: Is the refund unauthorized?  **gold: no**
- check: OK / problem:

### B22. contrastive_return_window

> {'policy': 'Returns are accepted only if the return request is submitted within 14 days of the purchase date.', 'case': "Sana bought a desk lamp on April 25, 2026. The return request was submitted on May 2, 2026. The order was paid by card and shipped to Sana's home address."}

- orig: Is this return request within the policy window?  **gold: yes**
- S1: Is this return request not within the policy window?  **gold: no**
- S2: Is it false that this return request is within the policy window?  **gold: no**
- S3: Is this return request outside the policy window?  **gold: no**
- check: OK / problem:

### B23. imdb

> Nothing is worse than the genocides of our world's history. This film attempts to describe the horror faced by one particular family - a common narrative device - in the atomic bomb world of Hiroshima. The most memorable parts are the graphic and saddening images that the people of Hiroshima face in the aftermath of wa ...

- orig: Is this movie review positive?  **gold: yes** (yes = The reviewer liked the film overall; no = The reviewer disliked the film overall)
- S1: Is this movie review not positive?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- S2: Is it false that this movie review is positive?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- S3: Did the reviewer dislike the film overall?  **gold: no** (yes = The reviewer disliked the film overall; no = The reviewer liked the film overall)
- check: OK / problem:

### B24. paws

> He makes what he spends on his back on his face .

- orig: Does this sentence mean the same thing: "What he spends on his bottom , he makes on his face ."  **gold: no** (yes = Same meaning, possibly reworded; no = Different meaning, even if most words match)
- S1: Does this sentence not mean the same thing: "What he spends on his bottom , he makes on his face ."  **gold: yes** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- S2: Is it false that this sentence means the same thing: "What he spends on his bottom , he makes on his face ."  **gold: yes** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- S3: Does this sentence mean something different from: "What he spends on his bottom , he makes on his face ."  **gold: yes** (yes = Different meaning, even if most words match; no = Same meaning, possibly reworded)
- check: OK / problem:

### B25. qnli

> {'document': 'Germany did so, and underground leader Piłsudski returned to Warsaw on 11 November and set up what became the Second Polish Republic, with Warsaw the capital.'}

- orig: Does the sentence contain the answer to this question: "What did Article 12 of the Allied Armistice terms require Germany to withdraw from?"  **gold: no**
- S1: Does the sentence not contain the answer to this question: "What did Article 12 of the Allied Armistice terms require Germany to withdraw from?"  **gold: yes**
- S2: Is it false that the sentence contains the answer to this question: "What did Article 12 of the Allied Armistice terms require Germany to withdraw from?"  **gold: yes**
- S3: Is the sentence missing the answer to this question: "What did Article 12 of the Allied Armistice terms require Germany to withdraw from?"  **gold: yes**
- check: OK / problem:
